from cProfile import run
from poker_engine import calculate_position


if __name__ == "__main__":
    hand = ['ah', 'as']
    base = ['3h', '3s', 'ac']

    def result(): return calculate_position(base, hand, [])
    run('result()', sort='cumtime')

