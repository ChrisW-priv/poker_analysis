#!/bin/python3

import unittest
import poker_engine
import numpy as np


def prep_cards(cards):
    cards = np.array([poker_engine.encode_card(card) for card in cards])
    return poker_engine.sort_numpy_array(cards)


class TestEngine(unittest.TestCase):
    def setUp(self):
        pass

    def test_interpretation(self):
        cases=( 
(['2d', '2s', '4s', '2h', '2c', '3h', '4s'], poker_engine.PokerHand.FourOfAKind),
(['2c', '3c', '4h', '6h', '7s', '8s', 'ts'], poker_engine.PokerHand.HighCard),
(['2c', '3c', '4h', '6h', 'ts', '7s', 'th'], poker_engine.PokerHand.Pair),
(['2c', '2h', '4h', '6h', '7s', '8s', 'th'], poker_engine.PokerHand.Pair),
(['2c', '3c', '4h', '6h', 'ts', 'th', 'td'], poker_engine.PokerHand.ThreeOfAKind),
(['2c', '4h', '6h', 'ts', 'th', 'td', '4d'], poker_engine.PokerHand.FullHouse),
(['2c', '3c', '4c', '7c', '6c', '5c', '8c'], poker_engine.PokerHand.StraightFlush),
(['2h', '4h', '4c', 'ac', 'ah', 'td', '8c'], poker_engine.PokerHand.TwoPair),
(['2h', '4h', '4c', 'ac', 'ah', 'td', 'tc'], poker_engine.PokerHand.TwoPair),
(['2c', '3s', '4s', '5s', '8d', '5c', '6c'], poker_engine.PokerHand.Straight),
(['as', '2c', '3s', '4s', '7d', '5c', '8c'], poker_engine.PokerHand.Straight),
(['2d', '3d', '4d', '5d', '6d', 'ts', '8c'], poker_engine.PokerHand.StraightFlush),
(['2d', '3d', '4d', '5d', '6s', 'td', '8c'], poker_engine.PokerHand.Flush),
(['2d', '3d', '4d', '5d', '9d', 'ts', '6c'], poker_engine.PokerHand.Flush),
(['8d', '9d', 'td', 'jd', 'qd', 'qc', 'kh'], poker_engine.PokerHand.StraightFlush)
               )

        for idx, (cards, eval) in enumerate(cases, 1):
            with self.subTest(f"Test case {idx}: {' '.join(cards)}"):
                cards = prep_cards(cards)
                interpreted = poker_engine.evaluate7cards(cards)[0]
                self.assertEqual(interpreted, eval, f"Expected: {eval}, Got: {interpreted}")

    def test_evaluation_of_same_hand(self):
        cases=( 
(['2d', '2s', '4s', '2h', '2c', '3h', '4s'], ['2d', '2s', '4d', '4h', '4c', '3h', '4s']),
(['2c', '3c', '4h', '6h', '7s', '8s', 'ts'], ['2c', '3c', '4h', '6h', '7s', '8s', 'as']),
(['2c', '3c', '4h', '6h', '7s', '8s', 'ts'], ['2c', '3c', '4h', '6h', '7s', '9s', 'ts']),
(['2c', '3c', '4h', '6h', '7s', '9s', 'ts'], ['2c', '3c', '4h', '6h', '8s', '9s', 'ts']),
(['2c', '3c', '4h', '6h', '7s', '8s', 'ts'], ['2c', '3c', '5h', '6h', '7s', '8s', 'ts']),
(['2c', '3c', '4h', '6h', '7s', 'ts', 'th'], ['2c', '3c', '4h', '6h', '7s', 'as', 'ah']),
(['2c', '2h', '4h', '6h', '7s', '8s', 'th'], ['2c', '2h', '4h', '6h', '7s', '8s', 'ah']),
(['2c', '2h', '4h', '6h', '7s', '8s', 'ah'], ['2c', '2h', '4h', '6h', '7s', 'ts', 'ah']),
(['2c', '3c', '4h', '6h', 'ts', 'th', 'td'], ['2c', '3c', '4h', '7h', 'ts', 'th', 'td']),
(['2c', '3c', '4h', '6h', 'ts', 'th', 'td'], ['2c', '3c', '4h', '6h', 'as', 'ah', 'ad']),
(['2c', '4h', '6h', 'ts', 'th', 'td', '4d'], ['2c', '5h', '6h', 'ts', 'th', 'td', '5d']),
(['2c', '6h', '6h', 'ts', 'th', 'td', '4d'], ['2c', '5h', '6h', 'as', 'ah', 'ad', '5d']),
(['2c', '3c', '4c', '5c', '6c', '7c', '7c'], ['2c', '3c', '4c', '5c', '6c', '7c', '8c']),
(['2h', '4h', '4c', 'ac', 'ah', 'td', '8c'], ['2h', '5h', '5c', 'ac', 'ah', 'td', '8c']),
(['2h', '6h', '6c', 'kc', 'kh', 'td', '8c'], ['2h', '5h', '5c', 'ac', 'ah', 'td', '8c']),
(['2h', '6h', '6c', 'kc', 'kh', 'td', '8c'], ['2h', '6h', '6c', 'kc', 'kh', 'td', 'ac']),
(['2h', '4h', '4c', 'ac', 'ah', 'td', 'tc'], ['2h', '4h', '4c', 'ac', 'ah', 'kd', 'kc']),
(['2c', '3s', '4s', '5s', '6d', '5c', '8c'], ['2c', '3s', '4s', '5s', '6d', '5c', '7c']),
(['as', '2c', '3s', '4s', '7d', '5c', '8c'], ['6s', '2c', '3s', '4s', '7d', '5c', '8c']),
(['2d', '3d', '4d', '5d', '6d', 'ts', '8c'], ['2d', '3d', '4d', '5d', '6d', '7d', '8c']),
(['2d', '3d', '4d', '5d', '8d', 'ad', '8c'], ['2d', '3d', '4d', '5d', '6d', 'ts', '8c']),
(['2d', '3d', '4d', '5d', '6d', '7c', '8c'], ['2d', '3d', '4d', '5d', '6d', '7d', '8c']),
               )

        for idx, (smaller, greater) in enumerate(cases, 1):
            with self.subTest(f"Test case {idx}: {cases[idx-1]}"):
                smaller_hand = prep_cards(smaller)
                greater_hand = prep_cards(greater)
                interpreted_value_smaller = poker_engine.evaluate7cards(smaller_hand)
                interpreted_value_greater = poker_engine.evaluate7cards(greater_hand)
                smaller_hand_strength = poker_engine.strength_of_hand(interpreted_value_smaller)
                greater_hand_strength = poker_engine.strength_of_hand(interpreted_value_greater)
                self.assertLess(smaller_hand_strength, greater_hand_strength)

    def test_calculate_position(self):
        community = ['8d', '9d', 'td', 'jd', 'qd']
        whole = ['ad', 'kd']
        result = poker_engine.calculate_position(community, whole, [])
        self.assertEqual(result, 100, f"Expected: 100, Got: {result}")


if __name__ == "__main__":
    unittest.main()
