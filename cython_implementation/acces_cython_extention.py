from poker_analysis import PokerEvaluator


if __name__ == '__main__':
    from cProfile import run
    hand = {('A', 'h'), ('A', 's')}
    base = {('3', 'h'), ('3', 's'), ('A', 'c')}

    evaluator = PokerEvaluator()
    evaluator.set_table_as(base)
    evaluator.update_hand(hand)
    result = evaluator.calculate_position
    # print(result())
    run('result()', sort='cumtime')
