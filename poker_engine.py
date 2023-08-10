from math import comb
import numpy as np
from itertools import combinations
from bisect import bisect_left

# 2,3,4,5,...9,t,j,k,a
RANKS = tuple(str(x) for x in range(2,9+1)) + ('t', 'j', 'q', 'k', 'a')
shift = 2
RANKS_ENCODED = tuple(range(shift, len(RANKS)+shift))
ACE_ENCODED_LAST = RANKS_ENCODED[-1]
ACE_ENCODED_ONE = 1
# clubs (♣), diamonds (♦), hearts (♥) and spades (♠)
SUITES = ('c', 'd', 'h', 's')
SUITES_ENCODED = tuple(range(len(SUITES)))
EXPONENT = 15
EVALUATION_TABLE_EXPONENTS = np.array([EXPONENT**i for i in range(6)])


def encode_card(card:str) -> tuple[int, int]:
    rank, suite = card
    rank_index = RANKS.index(rank)
    suite_index = SUITES.index(suite)
    rank_encoded = RANKS_ENCODED[rank_index]
    suite_encoded = SUITES_ENCODED[suite_index]
    return rank_encoded, suite_encoded


def decode_card(card:tuple[int, int]) -> str:
    rank, suite = card
    index_rank_decoded = bisect_left(RANKS_ENCODED, rank)
    index_suite_decoded = bisect_left(SUITES_ENCODED, suite)
    rank_decoded = RANKS[index_rank_decoded]
    suite_decoded = SUITES[index_suite_decoded]
    return str(rank_decoded) + str(suite_decoded)


def encode_cards_to_numpy(cards) -> np.ndarray:
    # converts list of tuples into map object of np.ndarrays
    numpied = map(np.array, cards)
    # converts map into actual array
    return np.array(list(numpied))


def construct_deck() -> set:
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


def total_number_of_positions_to_calculate(len_of_deck, len_community):
    positions_in_loop1 = comb(len_of_deck, 5-len_community)
    positions_in_loop2 = comb(len_of_deck-2, 2)
    return positions_in_loop1 * positions_in_loop2


def calculate_position(community_cards:list[str],
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

    community_cards_encoded = tuple(map(encode_card, community_cards))
    whole_cards_encoded = tuple(map(encode_card, whole_cards))
    excluded_cards_encoded = map(encode_card, excluded_cards)

    deck = construct_deck()
    set_community_cards = set(community_cards_encoded)
    set_whole_cards = set(whole_cards_encoded)
    set_excluded_cards = set(excluded_cards_encoded)
    deck = deck - set_community_cards - set_whole_cards - set_excluded_cards

    win = 0
    # total number of all positions is known before-hand 
    # total = total_number_of_positions_to_calculate(len(deck), len(community_cards)) 
    total = 0
    for table_addition in combinations(deck, 5-len(community_cards)):
        rest_of_deck = tuple(deck - set(table_addition))

        full_table = community_cards_encoded + table_addition

        our_seven_cards = np.array(full_table + whole_cards_encoded)
        our_cards_eval = eval7cards(our_seven_cards)
        our_cards_value = strength_of_hand(our_cards_eval)

        for enemy_cards in combinations(rest_of_deck, 2):
            enemy_seven_cards = np.array(full_table + enemy_cards)
            enemy_cards_eval = eval7cards(enemy_seven_cards)
            enemy_cards_value = strength_of_hand(enemy_cards_eval)
            if our_cards_value >= enemy_cards_value:
                win += 1
            else:
                pass
                # # here we could add information on what specific hands beat us
                # # for now we have a comment with print of what beats us
                # print("enemy cards:", tuple(map(decode_card, enemy_cards)), 
                #       "enemy eval:", enemy_cards_eval, 
                #       "our eval:", our_cards_eval)
            total += 1

    return round(win * 100 / total, 2)


def sort_numpy_array(array: np.ndarray) -> np.ndarray:
    # Sort the array based on the first value in each pair
    sorted_indices = np.argsort(array[:, 0])
    return array[sorted_indices]   


def handle_same_kind(state: int, zero_count: int) -> tuple[int, int]:
    """
    returns best state depending on what zero_count is and previous state
    aside from new state, returns code, what was changed
    ret value is coded as follows:
        - 0 for no change 
        - 1 for simple ev1 state set
        - 2 for simple ev2 state set
        - 3 for ev2=ev1, ev1 = val
    """
    if zero_count+1 == 2:
        if state == PokerHand.HighCard: return PokerHand.Pair, 1                # set ev1 to new pair rank
        if state == PokerHand.Pair: return PokerHand.TwoPair, 3                 # if there already was a pair then new one will have higher rank, set ev2 = ev1, ev1 = val
        if state == PokerHand.TwoPair: return PokerHand.TwoPair, 3              # if there already was a pair then new one will have higher rank, set ev2 = ev1, ev1 = val
        if state == PokerHand.ThreeOfAKind: return PokerHand.FullHouse, 2       # if there is ThreeOfAKind on board then just set ev2 to pair val
        if state == PokerHand.FullHouse: return PokerHand.FullHouse, 2          # if there is FullHouse then we just update the pair that makes it, so ev2 
    if zero_count+1 == 3:
        if state == PokerHand.HighCard: return PokerHand.ThreeOfAKind, 1
        if state == PokerHand.Pair: return PokerHand.FullHouse, 3
        if state == PokerHand.ThreeOfAKind: return PokerHand.FullHouse, 3
    if zero_count+1 == 4: return PokerHand.FourOfAKind, 1
    return state, 0


def interpret_sequence(ranks: np.ndarray) -> tuple[int, int, int]:
    best_hand = PokerHand.HighCard
    count_con_zero = 0
    count_con_one = 0
    last = ranks[0]
    eval_rank_better = 0
    eval_rank_lesser = 0
    for val in ranks[1:]:
        if val == last: 
            count_con_zero+=1
            last = val
            continue
        best_hand, code = handle_same_kind(best_hand, count_con_zero)
        if code == 1:
            eval_rank_better = last
        if code == 2:
            eval_rank_lesser = last
        if code == 3:
            eval_rank_lesser = eval_rank_better
            eval_rank_better = last

        count_con_zero = 0

        if val == last+1: 
            count_con_one += 1
            last = val
            continue

        # if it is not 0 or 1 then we check if we found Straight 
        if count_con_one+1 >= 5:
            best_hand = PokerHand.Straight
            eval_rank_better = last

        count_con_one = 0
        last = val 

    return best_hand, eval_rank_better, eval_rank_lesser


def eval7cards(sorted_cards:np.ndarray) -> tuple[int, int]:
    ranks = sorted_cards[:,0]
    # insert ace encoded as 1 at the beggining if there is ase in the deck
    if ranks[-1] == ACE_ENCODED_LAST:
        ranks = np.insert(ranks, 0, ACE_ENCODED_ONE) 

    suites = sorted_cards[:,1]
    suite_counts = np.zeros(4)
    for i in range(len(suites)):
        c = suites[i]
        suite_counts[c] += 1

    flush_suite = -1
    for i in range(4):
        if suite_counts[i] >= 5:
            flush_suite = i

    if flush_suite != -1:
        return eval_flush(ranks, suites, flush_suite)

    ranks_tailed = np.append(ranks,127)
    state_interpreted, better_rank, lesser_rank = interpret_sequence(ranks_tailed)

    if state_interpreted == PokerHand.HighCard:
        return PokerHand.HighCard, eval_high_card(ranks)
    if state_interpreted == PokerHand.Pair:
        return PokerHand.Pair, eval_pair(ranks, better_rank)
    if state_interpreted == PokerHand.ThreeOfAKind:
        return PokerHand.ThreeOfAKind, eval_three_of_a_kind(ranks, better_rank)
    if state_interpreted == PokerHand.TwoPair:
        return PokerHand.TwoPair, eval_two_pair(ranks, better_rank, lesser_rank)
    if state_interpreted == PokerHand.Straight:
        return PokerHand.Straight, eval_straight(better_rank)
    if state_interpreted == PokerHand.FullHouse:
        return PokerHand.FullHouse, eval_fullhouse(better_rank, lesser_rank)
    if state_interpreted == PokerHand.FourOfAKind:
        return PokerHand.FourOfAKind, eval_four_of_a_kind(ranks, better_rank)
    return PokerHand.ERROR, -1


def strength_of_hand(evaluation_of_7_cards) -> int:
    hand, eval = evaluation_of_7_cards
    return EVALUATION_TABLE_EXPONENTS[-1] * hand + eval


def eval_high_card(ranks) -> int:
    kickers = ranks[-5:]
    table = kickers * EVALUATION_TABLE_EXPONENTS[:-1]
    eval = table.sum()
    return eval


def eval_pair(ranks, rank_of_the_same_kind) -> int:
    eval = rank_of_the_same_kind * EVALUATION_TABLE_EXPONENTS[-2]
    next_eval = -3
    for i in range(7):
        val = ranks[-i-1]
        if val == rank_of_the_same_kind: continue
        eval += val * EVALUATION_TABLE_EXPONENTS[next_eval]
        next_eval -= 1
        if next_eval == -6: break
    return eval


def eval_three_of_a_kind(ranks, rank_of_the_same_kind) -> int:
    eval = rank_of_the_same_kind * EVALUATION_TABLE_EXPONENTS[-2]
    next_eval = -3
    for i in range(7):
        val = ranks[-i-1]
        if val == rank_of_the_same_kind: continue
        eval += val * EVALUATION_TABLE_EXPONENTS[next_eval]
        next_eval -= 1
        if next_eval == -6: break
    return eval


def eval_two_pair(ranks, card1, card2) -> int:
    eval = 0
    eval += card1 * EVALUATION_TABLE_EXPONENTS[-2]
    eval += card2 * EVALUATION_TABLE_EXPONENTS[-3]
    for i in range(7):
        val = ranks[-i-1]
        if val in (card1, card2): continue
        eval += val * EVALUATION_TABLE_EXPONENTS[-4]
        break
    return eval
    

def eval_straight(card1) -> int:
    return card1


def eval_fullhouse(card1, card2) -> int:
    eval = 0
    eval += card1 * EVALUATION_TABLE_EXPONENTS[-2]
    eval += card2 * EVALUATION_TABLE_EXPONENTS[-3]
    return eval


def eval_four_of_a_kind(ranks, rank_of_the_same_kind) -> int:
    eval = rank_of_the_same_kind * EVALUATION_TABLE_EXPONENTS[-2]
    for i in range(7):
        val = ranks[-i-1]
        if val == rank_of_the_same_kind: continue
        eval += val * EVALUATION_TABLE_EXPONENTS[-3]
        break
    return eval


def eval_flush(ranks, suites, flush_suite) -> tuple[int, int]:
    flush_mask = np.where(suites == flush_suite)[0]
    ranks_in_flush = ranks[flush_mask]
    ranks_in_flush = np.append(ranks_in_flush, 127)
    interpret_state, highest_rank, _ = interpret_sequence(ranks_in_flush)
    if interpret_state == PokerHand.Straight:
        return PokerHand.StraightFlush, highest_rank
    return PokerHand.Flush, ranks_in_flush[-1]

