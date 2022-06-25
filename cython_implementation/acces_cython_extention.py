from poker_analysis import calculate_position, set_table_as, update_hand


if __name__ == '__main__':
    from cProfile import run
    hand = {('A', 'h'), ('A', 's')}
    base = {('3', 'h'), ('3', 's'), ('A', 'c')}

    set_table_as(base)
    update_hand(hand)
    result = calculate_position
    # print(result())
    run('result()', sort='cumtime')
