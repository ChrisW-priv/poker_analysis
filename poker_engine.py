from enum import Enum
import numpy as np
from functools import reduce

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

    # Sort the array based on the first value in each pair
    sorted_indices = np.argsort(current_hand[:, 0])
    sorted_cards = current_hand[sorted_indices]   

    result = eval7cards(sorted_cards)


def reduce_the_same_kind(acc, val):
    state, last, count = acc
    if val == last: return state, val, count + 1
    if last == 0:
        if count+1 == 4: return PokerHands.FourOfAKind, val, 1
        if state == PokerHands.HighCard:
            if count+1 == 2: return PokerHands.Pair, val, 1
            if count+1 == 3: return PokerHands.ThreeOfAKind, val, 1
        if state == PokerHands.Pair:
            if count+1 == 2: return PokerHands.TwoPair, val, 1
            if count+1 == 3: return PokerHands.FullHouse, val, 1
        if state == PokerHands.ThreeOfAKind:
            if count+1 == 2: return PokerHands.FullHouse, val, 1
            if count+1 == 3: return PokerHands.FullHouse, val, 1
    return state, val, 1


def eval7cards(sorted_cards:np.ndarray):
    ranks = sorted_cards[:,0]
    suites = sorted_cards[:,1]
    consecutive_ranks_diff = np.diff(ranks)
    suite_counts = np.array([(suites == value).sum() for value in range(4)])
    flush_present = np.any(suite_counts >= 5)

    result = reduce(reduce_the_same_kind,
                    consecutive_ranks_diff[1:], 
                    (PokerHands.HighCard, consecutive_ranks_diff[0], 1))


