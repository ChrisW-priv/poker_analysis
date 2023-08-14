import numpy as np
from itertools import combinations
from bisect import bisect_left
from multiprocessing import Pool
from functools import partial

# 2,3,4,5,...9,t,j,k,a
RANKS = tuple(str(x) for x in range(2,9+1)) + ('t', 'j', 'q', 'k', 'a')
shift = 2
RANKS_ENCODED = tuple(range(shift, len(RANKS)+shift))
ACE_ENCODED_LAST = RANKS_ENCODED[-1]
MINIMUM_FOR_ACE = ACE_ENCODED_LAST << 2
ACE_ENCODED_ONE = 1 << 2
MASK_SUITES = 0x3
# clubs (♣), diamonds (♦), hearts (♥) and spades (♠)
SUITES = ('c', 'd', 'h', 's')
SUITES_ENCODED = tuple(range(len(SUITES)))
EXPONENT = 15
EVALUATION_TABLE_EXPONENTS = np.array([EXPONENT**i for i in range(6)])


def encode_card(card:str) -> int:
    rank, suite = card
    rank_index = RANKS.index(rank)
    suite_index = SUITES.index(suite)
    rank_encoded = RANKS_ENCODED[rank_index]
    suite_encoded = SUITES_ENCODED[suite_index]
    encoded = rank_encoded << 2 | suite_encoded
    return encoded


def decode_card(card: int) -> str:
    suite = card & MASK_SUITES
    rank = card >> 2
    index_rank_decoded = bisect_left(RANKS_ENCODED, rank)
    index_suite_decoded = bisect_left(SUITES_ENCODED, suite)
    rank_decoded = RANKS[index_rank_decoded]
    suite_decoded = SUITES[index_suite_decoded]
    return str(rank_decoded) + str(suite_decoded)


def construct_deck() -> set[int]:
    return set(encode_card(rank+suite) for rank in RANKS for suite in SUITES)


class PokerHand(int):
    ERROR = -1
    HighCard = 1
    Pair = 2
    TwoPair = 3
    ThreeOfAKind = 4
    Straight = 5
    Flush = 6
    FullHouse = 7
    FourOfAKind = 8
    StraightFlush = 9


def assert_correctness(community_cards:list[str],
                       whole_cards:list[str],
                       excluded_cards:list[str]):
    # assert correct size
    assert(len(whole_cards) == 2)
    assert(len(community_cards) <= 5)
    # assert no duplicates between any of 3 sets
    assert(all(card not in whole_cards for card in excluded_cards))
    assert(all(card not in community_cards for card in excluded_cards))
    assert(all(card not in community_cards for card in whole_cards))
    # assert no duplicates in any of 3 sets
    assert(len(set(community_cards)) == len(community_cards))
    assert(len(set(whole_cards)) == len(whole_cards))
    assert(len(set(excluded_cards)) == len(excluded_cards))


def calculate_for_all_possible_additions(deck: set[int], 
                                         community_cards_encoded: tuple[int],
                                         whole_cards_encoded: tuple[int],
                                         table_addition: tuple[int]) -> tuple[int, int]:
    rest_of_deck = tuple(deck - set(table_addition))

    full_table = community_cards_encoded + table_addition

    our_seven_cards = sorted(full_table + whole_cards_encoded)
    our_seven_cards_array = bytearray(8)
    for i in range(7):
        our_seven_cards_array[i + 1] = our_seven_cards[i]
    our_cards_evaluate = evaluate7cards(our_seven_cards_array)
    our_cards_value = strength_of_hand(our_cards_evaluate)

    win = 0
    total = 0
    for enemy_cards in combinations(rest_of_deck, 2):
        enemy_seven_cards = sorted(full_table + enemy_cards)
        enemy_seven_cards_array = bytearray(8)
        for i in range(7):
            enemy_seven_cards_array[i + 1] = enemy_seven_cards[i]
        enemy_cards_evaluate = evaluate7cards(enemy_seven_cards_array)
        enemy_cards_value = strength_of_hand(enemy_cards_evaluate)
        if our_cards_value >= enemy_cards_value:
            win += 1
        else:
            pass
            # # here we could add information on what specific hands beat us
            # # for now we have a comment with print of what beats us
            # print("enemy cards:", tuple(map(decode_card, enemy_cards)), 
            #       "enemy evaluate:", enemy_cards_evaluate, 
            #       "our evaluate:", our_cards_evaluate)
        total += 1
    return win, total


def calculate_position(community_cards:list[str],
                       whole_cards:list[str],
                       excluded_cards:list[str]):
    assert_correctness(community_cards, whole_cards, excluded_cards)
    community_cards_encoded = tuple(map(encode_card, community_cards))
    whole_cards_encoded = tuple(map(encode_card, whole_cards))
    excluded_cards_encoded = map(encode_card, excluded_cards)

    deck = construct_deck()
    set_community_cards = set(community_cards_encoded)
    set_whole_cards = set(whole_cards_encoded)
    set_excluded_cards = set(excluded_cards_encoded)
    deck = deck - set_community_cards - set_whole_cards - set_excluded_cards
    
    winning = 0
    total = 0

    unary = partial(calculate_for_all_possible_additions, deck, community_cards_encoded, whole_cards_encoded)

    with Pool() as pool:
        results = pool.imap_unordered(unary, combinations(deck, 5-len(community_cards)))

        for win, tot in results:
            winning += win
            total += tot

    return round(winning * 100 / total, 2)


def handle_same_kind(state: int, value, better_rank, lesser_rank) -> tuple[int, int]:
    """
    returns best state depending on what zero_count is and previous state
    aside from new state, returns code, what was changed
    ret value is coded as follows:
        - 0 for no change 
        - 1 for simple ev1 state set
        - 2 for simple ev2 state set
        - 3 for ev2=ev1, ev1 = val
    """
    if state == PokerHand.HighCard: 
        return PokerHand.Pair, 1
    if state == PokerHand.Pair:
        if value == better_rank: 
            return PokerHand.ThreeOfAKind, 1
        return PokerHand.TwoPair, 3
    if state == PokerHand.TwoPair:
        if value == better_rank: 
            return PokerHand.FullHouse, 1
        return PokerHand.TwoPair, 3
    if state == PokerHand.ThreeOfAKind:
        if value == better_rank: 
            return PokerHand.FourOfAKind, 1
        return PokerHand.FullHouse, 2
    if state == PokerHand.FullHouse:
        if value == better_rank: 
            return PokerHand.FourOfAKind, 1
        if value == lesser_rank: 
            return PokerHand.FullHouse, 3
        return PokerHand.FullHouse, 2
    return state, 0


def interpret_sequence(ranks: bytearray) -> tuple[int, int, int]:
    best_hand = PokerHand.HighCard
    count_con_one = 0
    last = ranks[0]
    better_rank = 0
    lesser_rank = 0
    for val in ranks[1:]:
        if val == last:
            best_hand, code = handle_same_kind(best_hand, val, better_rank, lesser_rank)
            if code == 1:
                better_rank = val
            if code == 2:
                lesser_rank = val
            if code == 3:
                lesser_rank = better_rank
                better_rank = val
        elif val == last + 1:
            count_con_one += 1
            if count_con_one >= 4:
                best_hand = PokerHand.Straight
                better_rank = val
        else:
            count_con_one = 0
        last = val

    return best_hand, better_rank, lesser_rank


def evaluate7cards(sorted_cards: bytearray) -> tuple[int, int]:
    if sorted_cards[-1] >= MINIMUM_FOR_ACE:
        sorted_cards[0] = ACE_ENCODED_ONE | (sorted_cards[-1] & MASK_SUITES)

    ranks = bytearray( ((card >> 2) for card in sorted_cards) )
    suites = bytearray( (card & MASK_SUITES for card in sorted_cards) )

    suite_counts = np.zeros(4)
    for suite in suites:
        suite_counts[suite] += 1

    flush_suite = -1
    for i in range(4):
        if suite_counts[i] >= 5:
            flush_suite = i

    if flush_suite != -1:
        return evaluate_flush(ranks, suites, flush_suite)

    state_interpreted, better_rank, lesser_rank = interpret_sequence(ranks)

    if state_interpreted == PokerHand.HighCard:
        return PokerHand.HighCard, evaluate_high_card(ranks)
    if state_interpreted == PokerHand.Pair:
        return PokerHand.Pair, evaluate_pair(ranks, better_rank)
    if state_interpreted == PokerHand.ThreeOfAKind:
        return PokerHand.ThreeOfAKind, evaluate_three_of_a_kind(ranks, better_rank)
    if state_interpreted == PokerHand.TwoPair:
        return PokerHand.TwoPair, evaluate_two_pair(ranks, better_rank, lesser_rank)
    if state_interpreted == PokerHand.Straight:
        return PokerHand.Straight, evaluate_straight(better_rank)
    if state_interpreted == PokerHand.FullHouse:
        return PokerHand.FullHouse, evaluate_fullhouse(better_rank, lesser_rank)
    if state_interpreted == PokerHand.FourOfAKind:
        return PokerHand.FourOfAKind, evaluate_four_of_a_kind(ranks, better_rank)
    return PokerHand.ERROR, -1


def strength_of_hand(evaluateuation_of_7_cards) -> int:
    hand, evaluate = evaluateuation_of_7_cards
    return EVALUATION_TABLE_EXPONENTS[-1] * hand + evaluate


def evaluate_high_card(ranks) -> int:
    evaluate = 0
    for i in range(5):
        evaluate += ranks[-1-i] * EVALUATION_TABLE_EXPONENTS[-i-2]
    return evaluate


def evaluate_pair(ranks, rank_of_the_same_kind) -> int:
    evaluate = rank_of_the_same_kind * EVALUATION_TABLE_EXPONENTS[-2]
    next_evaluate = -3
    for i in range(7):
        val = ranks[-i-1]
        if val == rank_of_the_same_kind: continue
        evaluate += val * EVALUATION_TABLE_EXPONENTS[next_evaluate]
        next_evaluate -= 1
        if next_evaluate == -6: break
    return evaluate


def evaluate_three_of_a_kind(ranks, rank_of_the_same_kind) -> int:
    evaluate = rank_of_the_same_kind * EVALUATION_TABLE_EXPONENTS[-2]
    next_evaluate = -3
    for i in range(7):
        val = ranks[-i-1]
        if val == rank_of_the_same_kind: continue
        evaluate += val * EVALUATION_TABLE_EXPONENTS[next_evaluate]
        next_evaluate -= 1
        if next_evaluate == -6: break
    return evaluate


def evaluate_two_pair(ranks, card1, card2) -> int:
    evaluate = 0
    evaluate += card1 * EVALUATION_TABLE_EXPONENTS[-2]
    evaluate += card2 * EVALUATION_TABLE_EXPONENTS[-3]
    ret = ranks[-1]
    if ret == card1 or ret == card2:
        ret = ranks[-3]
    if ret == card1 or ret == card2:
        ret = ranks[-5]
    evaluate += ret * EVALUATION_TABLE_EXPONENTS[-4]
    return evaluate
    

def evaluate_straight(card1) -> int:
    return card1


def evaluate_fullhouse(card1, card2) -> int:
    evaluate = 0
    evaluate += card1 * EVALUATION_TABLE_EXPONENTS[-2]
    evaluate += card2 * EVALUATION_TABLE_EXPONENTS[-3]
    return evaluate


def evaluate_four_of_a_kind(ranks, rank_of_the_same_kind) -> int:
    evaluate = rank_of_the_same_kind * EVALUATION_TABLE_EXPONENTS[-2]
    index = -1
    if ranks[-1] == rank_of_the_same_kind: 
        index = -5

    evaluate += ranks[index] * EVALUATION_TABLE_EXPONENTS[-3]
    return evaluate


def evaluate_flush(ranks, suites, flush_suite) -> tuple[int, int]:
    last = next(ranks[i] for i, suite in enumerate(suites) if suite == flush_suite)
    consec = 0
    ret = 0
    for i, suite in enumerate(suites):
        if suite == flush_suite:
            rank = ranks[i]
            if rank == last + 1:
                consec += 1
                if consec >= 4:
                    ret = rank
            else: consec = 0
            last = rank

    if ret:
        return PokerHand.StraightFlush, ret
    return PokerHand.Flush, last

