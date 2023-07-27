from enum import Enum
import numpy as np
from functools import reduce
from dataclasses import dataclass

# 2,3,4,5,...9,t,j,k,a
RANKS = tuple(str(x) for x in range(2,9+1)) + ('t', 'j', 'q', 'k', 'a')
RANKS_ENCODED = range(len(RANKS))
# clubs (♣), diamonds (♦), hearts (♥) and spades (♠)
SUITES = ('c', 'd', 'h', 's')
SUITES_ENCODED = range(len(SUITES))

def encode_card(card:str) -> np.ndarray:
    rank, suite = card
    rank_encoded = RANKS.index(rank)
    suite_encoded = SUITES.index(suite)
    return np.array([rank_encoded, suite_encoded])


def construct_deck():
    return set(encode_card(rank+suite) for rank in RANKS for suite in SUITES)


@dataclass(order=True)
class PokerHands(Enum):
    HighCard = 1
    Pair = 2
    TwoPair = 3
    ThreeOfAKind = 4
    Straight = 5
    Flush = 6
    FullHouse = 7
    FourOfAKind = 8
    StraightFlush = 9

    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return self.value == other.value
        return NotImplemented


def calculate_position(community_cards:list[str],
                       whole_cards:list[str],
                       excluded_cards:list[str]):
    assert(len(whole_cards) == 2)

    deck = construct_deck()
    set_community_cards = set(map(encode_card, community_cards))
    set_whole_cards = set(map(encode_card, whole_cards))
    set_excluded_cards = set(map(encode_card, excluded_cards))

    deck = deck - set_community_cards - set_whole_cards - set_excluded_cards

    arr_community_cards = np.array(community_cards)
    arr_whole_cards = np.array(whole_cards)

    current_hand = arr_community_cards + arr_whole_cards
    sorted_cards = sort_numpy_array(current_hand)

    result = eval7cards(sorted_cards)


def sort_numpy_array(array: np.ndarray) -> np.ndarray:
    # Sort the array based on the first value in each pair
    sorted_indices = np.argsort(array[:, 0])
    return array[sorted_indices]   

def handle_same_kind(state, zero_count):
    if zero_count+1 == 4: state = PokerHands.FourOfAKind
    if state == PokerHands.HighCard:
        if zero_count+1 == 2: state = PokerHands.Pair
        if zero_count+1 == 3: state = PokerHands.ThreeOfAKind
    if state == PokerHands.Pair:
        if zero_count+1 == 2: state = PokerHands.TwoPair
        if zero_count+1 == 3: state = PokerHands.FullHouse
    if state == PokerHands.ThreeOfAKind:
        if zero_count+1 == 2: state = PokerHands.FullHouse
        if zero_count+1 == 3: state = PokerHands.FullHouse

    return state


def reduce_the_same_kind(acc, val):
    best_hand, count_con_zero, count_con_one = acc
    if val == 0: return best_hand, count_con_zero+1, count_con_one
    if val == 1:
        count_con_one += 1
        if count_con_one+1 == 5: return PokerHands.Straight, count_con_zero, count_con_one+1
        state = handle_same_kind(best_hand, count_con_zero)
        return state, 0, count_con_one
    # if it is not 0 or 1
    state = handle_same_kind(best_hand, count_con_zero)
    return state, 0, 0


def eval7cards(sorted_cards:np.ndarray):
    ranks = sorted_cards[:,0]
    suites = sorted_cards[:,1]
    consecutive_ranks_diff = np.diff(ranks)
    suite_counts = np.array([(suites == value).sum() for value in range(4)])
    flush_present = np.any(suite_counts >= 5)

    result = reduce(reduce_the_same_kind,
                    consecutive_ranks_diff[1:], (
                        PokerHands.HighCard,                # state
                        consecutive_ranks_diff[0] == 0,     # count of zeros
                        consecutive_ranks_diff[0] == 1)     # count of ones
                    )

    state:PokerHands = result[0]
    if flush_present and state < PokerHands.Flush: state = PokerHands.Flush
    return state

