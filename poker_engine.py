from enum import Enum
import numpy as np
from functools import reduce
from itertools import combinations

# 2,3,4,5,...9,t,j,k,a
RANKS = tuple(str(x) for x in range(2,9+1)) + ('t', 'j', 'q', 'k', 'a')
RANKS_ENCODED = range(len(RANKS))
ACE_ENCODED_LAST = RANKS_ENCODED[-1]
ACE_ENCODED_ONE = -1
# clubs (♣), diamonds (♦), hearts (♥) and spades (♠)
SUITES = ('c', 'd', 'h', 's')
SUITES_ENCODED = range(len(SUITES))
EVALUATION_TABLE_EXPONENTS = tuple(15**i for i in range(5))


def encode_card(card:str) -> tuple[int, int]:
    rank, suite = card
    rank_encoded = RANKS.index(rank)
    suite_encoded = SUITES.index(suite)
    return rank_encoded, suite_encoded


def decode_card(card:tuple[int, int]) -> str:
    rank, suite = card
    index_rank_decoded = RANKS_ENCODED.index(rank)
    index_suite_decoded = SUITES_ENCODED.index(suite)
    rank_decoded = RANKS[index_rank_decoded]
    suite_decoded = SUITES[index_suite_decoded]
    return str(rank_decoded) + str(suite_decoded)


def construct_deck() -> set:
    return set(encode_card(rank+suite) for rank in RANKS for suite in SUITES)


class PokerHand(int, Enum):
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


def encode_cards_to_numpy(cards) -> np.ndarray:
    # converts list of tuples into map object of np.ndarrays
    numpied = map(np.array, cards)
    # converts map into actual array
    return np.array(list(numpied))


def calculate_position(community_cards:list[str],
                       whole_cards:list[str],
                       excluded_cards:list[str]):
    assert(len(whole_cards) == 2)
    assert(len(community_cards) <= 5)
    assert(all(card not in whole_cards for card in excluded_cards))
    assert(all(card not in community_cards for card in excluded_cards))
    assert(all(card not in community_cards for card in whole_cards))

    arr_community_cards = encode_cards_to_numpy(map(encode_card, community_cards))
    arr_whole_cards = encode_cards_to_numpy(map(encode_card, whole_cards))

    deck = construct_deck()
    set_community_cards = set(map(encode_card, community_cards))
    set_whole_cards = set(map(encode_card, whole_cards))
    set_excluded_cards = set(map(encode_card, excluded_cards))
    deck = deck - set_community_cards - set_whole_cards - set_excluded_cards

    win = 0
    total = 0
    for table_addition in combinations(deck, 5-len(community_cards)):
        rest_of_deck = tuple(deck - set(table_addition))

        if len(community_cards) == 5:
            full_table = arr_community_cards
        else:
            arr_table_addition = encode_cards_to_numpy(table_addition)
            full_table = np.concatenate((arr_community_cards, arr_table_addition))

        our_seven_cards = np.concatenate((full_table, arr_whole_cards))
        our_cards_eval = eval7cards(our_seven_cards)
        our_cards_value = strength_of_hand(our_cards_eval)

        for enemy_cards in combinations(rest_of_deck, 2):
			# here the code could be set to run on multiple cores to calculate values for different enemy cards
            arr_enemy_cards = encode_cards_to_numpy(enemy_cards)
            enemy_seven_cards = np.concatenate((full_table, arr_enemy_cards))
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


def handle_same_kind(state, zero_count):
    if zero_count+1 == 2:
        if state is PokerHand.HighCard: return PokerHand.Pair
        if state is PokerHand.Pair: return PokerHand.TwoPair
        if state is PokerHand.ThreeOfAKind: return PokerHand.FullHouse
    if zero_count+1 == 3:
        if state is PokerHand.HighCard: return PokerHand.ThreeOfAKind
        if state is PokerHand.Pair or state is PokerHand.ThreeOfAKind:
            return PokerHand.FullHouse
    if zero_count+1 == 4: return PokerHand.FourOfAKind
    return state


def reduce_sequence(acc, val):
    best_hand, count_con_zero, count_con_one = acc

    if val == 0: return best_hand, count_con_zero+1, count_con_one
    best_hand = handle_same_kind(best_hand, count_con_zero)

    if val == 1: return best_hand, 0, count_con_one + 1

    # if it is not 0 or 1 then we check if we found Straight 
    if count_con_one+1 >= 5: return PokerHand.Straight, count_con_zero, count_con_one

    return best_hand, 0, 0


def interpret_sequence(consevutive_ranks_diff: np.ndarray) -> PokerHand:
    result = reduce(reduce_sequence,
                    consevutive_ranks_diff[1:], (
                        PokerHand.HighCard,                 # state
                        consevutive_ranks_diff[0] == 0,     # count of zeros
                        consevutive_ranks_diff[0] == 1)     # count of ones
                    )
    return result[0]


def eval_pair(ranks, consecutive_ranks_diff) -> int:
    zero_mask = consecutive_ranks_diff == 0
    zero_indexes = np.where(zero_mask)[0]
    index_of_zero = zero_indexes[0]
    rank_of_the_same_kind = ranks[index_of_zero]
    kickers = ranks[~zero_mask][-2:]
    eval = rank_of_the_same_kind * EVALUATION_TABLE_EXPONENTS[-2]
    eval += kickers[-1] * EVALUATION_TABLE_EXPONENTS[-3]
    eval += kickers[-2] * EVALUATION_TABLE_EXPONENTS[-4]
    return eval


def eval_three_of_a_kind(ranks, consecutive_ranks_diff) -> int:
    zero_mask = consecutive_ranks_diff == 0
    zero_indexes = np.where(zero_mask)[0]
    index_of_zero = zero_indexes[0]
    rank_of_the_same_kind = ranks[index_of_zero]
    kickers = ranks[~zero_mask][-3:]
    eval = rank_of_the_same_kind * EVALUATION_TABLE_EXPONENTS[-2]
    eval += kickers[-1] * EVALUATION_TABLE_EXPONENTS[-3]
    eval += kickers[-2] * EVALUATION_TABLE_EXPONENTS[-4]
    eval += kickers[-3] * EVALUATION_TABLE_EXPONENTS[-5]
    return eval


def eval_two_pair(ranks, consecutive_ranks_diff) -> int:
    zero_mask = consecutive_ranks_diff == 0
    zero_indexes = np.where(zero_mask)[0]
    index_of_higher_pair = zero_indexes[-1]
    index_of_lower_pair = zero_indexes[-2]
    higher_pair_rank = ranks[index_of_higher_pair]
    lower_pair_rank = ranks[index_of_lower_pair]
    kicker = ranks[~zero_mask][-1]
    eval = higher_pair_rank * EVALUATION_TABLE_EXPONENTS[-2]
    eval += lower_pair_rank * EVALUATION_TABLE_EXPONENTS[-3]
    eval += kicker * EVALUATION_TABLE_EXPONENTS[-4]
    return eval
    

def eval_straight(ranks, consecutive_ranks_diff) -> int:
    cumulative = np.cumsum(consecutive_ranks_diff)
    index_of_termination = np.argmax(consecutive_ranks_diff == first_to_terminate_sequence)
    highest_rank = ranks[index_of_termination - 1]
    return highest_rank


def eval_fullhouse(ranks, consecutive_ranks_diff) -> int:
    """
    have to consider several cases here: 
        - aaabbcd (three of a kind first)
        - aabbbcd (three of a kind second)
        - aabbbcc (three of a kind surrounded by pairs)
        - aaccbbb (three of a kind last)
    """
    zero_mask = np.where(consecutive_ranks_diff==0)[0]
    last_elem = zero_mask[-1]
    second_last = zero_mask[-2]
    first_elem = zero_mask[-3]
    if last_elem == second_last+1:
        three = ranks[last_elem]
        pair = ranks[first_elem]
    else:
        three = ranks[first_elem]
        pair = ranks[last_elem]
    evaluation = 1 * pair + 100 * three
    return evaluation


def eval_four_of_a_kind(ranks, consecutive_ranks_diff) -> int:
    """
    have to consider several cases here: 
        - aaaabbc (there is more than one "same kind")
        - bbaaaac (there is more than one "same kind")
        - aaaabcd (there is not more than one "same kind")
    """
    zero_mask = np.where(consecutive_ranks_diff==0)[0]
    last_elem = zero_mask[-1]
    second_last = zero_mask[-2]
    first_elem = zero_mask[-3]
    if last_elem == second_last+1:
        four = ranks[last_elem]
    else:
        four = ranks[first_elem]
    return four


def eval_flush(ranks, consecutive_ranks_diff, suites, flush_suite) -> tuple[PokerHand, int]:
    flush_mask = np.where(suites == flush_suite)[0]
    ranks_in_flush = ranks[flush_mask]
    flush_rank_diff = np.diff(ranks_in_flush, append=127)
    interpret = interpret_sequence(flush_rank_diff)
    if interpret is PokerHand.Straight:
        one_mask = np.where(consecutive_ranks_diff==1)[0]
        index_of_highest_rank = one_mask[-1]+1
        highest_rank = ranks[index_of_highest_rank]
        return PokerHand.StraightFlush, highest_rank
    return PokerHand.Flush, ranks_in_flush[-1]


def eval7cards(sorted_cards:np.ndarray) -> tuple[PokerHand, int]:
    ranks = sorted_cards[:,0]
    if ranks[-1] == ACE_ENCODED_LAST:
        ranks = np.insert(ranks, 0, ACE_ENCODED_ONE) # insert ace encoded as 1 at the beggining

    consecutive_ranks_diff = np.diff(ranks, append=127)

    # see if there is a flush
    suites = sorted_cards[:,1]
    suite_counts = np.array([(suites == value).sum() for value in range(4)])
    suite_count_mask = np.where(suite_counts >= 5)[0]
    flush_suite = -1
    if suite_count_mask.size != 0:
        flush_suite = suite_count_mask[0]

    if flush_suite != -1:
        return eval_flush(ranks, consecutive_ranks_diff, suites, flush_suite)

    state_interpreted = interpret_sequence(consecutive_ranks_diff)
    high_card = ranks[-1]

    if state_interpreted is PokerHand.HighCard:
        return PokerHand.HighCard, high_card
    if state_interpreted is PokerHand.Pair:
        return PokerHand.Pair, eval_pair(ranks, consecutive_ranks_diff)
    if state_interpreted is PokerHand.ThreeOfAKind:
        return PokerHand.ThreeOfAKind, eval_three_of_a_kind(ranks, consecutive_ranks_diff)
    if state_interpreted is PokerHand.TwoPair:
        return PokerHand.TwoPair, eval_two_pair(ranks, consecutive_ranks_diff)
    if state_interpreted is PokerHand.Straight:
        return PokerHand.Straight, eval_straight(ranks, consecutive_ranks_diff)
    if state_interpreted is PokerHand.FullHouse:
        return PokerHand.FullHouse, eval_fullhouse(ranks, consecutive_ranks_diff)
    if state_interpreted is PokerHand.FourOfAKind:
        return PokerHand.FourOfAKind, eval_four_of_a_kind(ranks, consecutive_ranks_diff)
    return PokerHand.ERROR, -1


def strength_of_hand(evaluation_of_7_cards):
    hand, eval = evaluation_of_7_cards
    return 100_000_000 * hand + eval

