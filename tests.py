#!/bin/python3

import unittest
import poker_engine
import numpy as np


class TestEngine(unittest.TestCase):
    def setUp(self):
        pass

    def test_7cards(self):
        cases=( 
(['2d', '2s', '4s', '2h', '2c', '3h', '4s'], poker_engine.PokerHands.FourOfAKind),
(['2c', '3c', '4h', '6h', '7s', '8s', 'ts'], poker_engine.PokerHands.HighCard),
(['2c', '3c', '4h', '6h', '7s', 'ts', 'th'], poker_engine.PokerHands.Pair),
(['2c', '3c', '4h', '6h', 'ts', 'th', 'td'], poker_engine.PokerHands.ThreeOfAKind),
(['2c', '4h', '6h', 'ts', 'th', 'td', '4d'], poker_engine.PokerHands.FullHouse),
(['2c', '3c', '4c', '5c', '6c', '7c', '8c'], poker_engine.PokerHands.StraightFlush),
(['2h', '4h', '4c', 'ac', 'ah', 'td', '8c'], poker_engine.PokerHands.TwoPair),
(['2c', '3s', '4s', '5s', '6d', '5c', '8c'], poker_engine.PokerHands.Straight),
(['2d', '3d', '4d', '5d', '6d', 'ts', '8c'], poker_engine.PokerHands.StraightFlush),
(['2d', '3d', '4d', '5d', '2s', 'ts', '8c'], poker_engine.PokerHands.Flush)
               )

        for idx, (cards, eval) in enumerate(cases, 1):
            with self.subTest(f"Test case {idx}: {' '.join(cards)}"):
                cards = np.array([poker_engine.encode_card(card) for card in cards])
                cards = poker_engine.sort_numpy_array(cards)
                result = poker_engine.eval7cards(cards)
                self.assertEqual(result, eval, f"Expected: {eval}, Got: {result}")


if __name__ == "__main__":
    unittest.main()
