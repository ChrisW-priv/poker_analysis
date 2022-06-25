from itertools import combinations

# types of hand:
# 'highest_card','pair','two_pair','three_of_a_kind','straight','flush','full_house','four_of_a_kind','straight_flush'
# card suites:
# diamonds (♦), clubs (♣), hearts (♥) and spades (♠)


def memo(f):
	memo_table = {}

	def wrapper(arg):
		if arg in memo_table:
			return memo_table[arg]
		else:
			val = f(arg)
			memo_table[arg] = val
			return val

	return wrapper


SUITES = ('d', 'c', 'h', 's')
CARD_VALUES = {
	'J': 11,
	'D': 12,
	'K': 13,
	'A': 14,
	**{str(n): n for n in range(2, 11)}
}


def reset_deck():
	return set(_normalize_card((num, col)) for num in CARD_VALUES for col in SUITES)


def _normalize_card(card):
	"""takes a tuple (str, str) and normalises it to make it consistent across code, returns (int, int) tuple"""
	number = CARD_VALUES[card[0]]
	color = SUITES.index(card[1])
	return number, color


_table = tuple()
_hand = tuple()
deck = reset_deck()


def set_table_as(table: set):
	"""resets table of community cards to given set of cards"""
	global deck, _table
	table = set(_normalize_card(card) for card in table)
	_table = tuple(table)
	deck -= table


def update_table(card):
	"""adds normalised card to a table of community cards"""
	global deck, _table
	card = _normalize_card(card)
	_table += card
	deck -= card


def update_hand(players_hand):
	"""normalises cards and sets them as current cards of a player"""
	global deck, _hand
	players_hand = set(_normalize_card(card) for card in players_hand)
	_hand = tuple(players_hand)
	deck -= players_hand


def positions_to_calculate():
	"""calculates how many positions are there to consider during evaluation"""
	"""returns number of possible combinations of full table times number of combinations for enemy cards"""

	n_cards_left_in_deck = len(deck)
	n_cards_left_to_full_table = 5 - len(_table)
	multiplier = 1
	denominator = 1
	for i in range(n_cards_left_to_full_table):
		multiplier *= (n_cards_left_in_deck - i)
		denominator *= (i+1)

	cards_to_choose_from_for_enemy = n_cards_left_in_deck - n_cards_left_to_full_table
	for i in range(2):
		multiplier *= (cards_to_choose_from_for_enemy - i)
		denominator *= (i+1)

	return multiplier//denominator


def calculate_position():
	"""calculates percentage of how many times we win or make a draw compered to all position that we consider"""

	def value_of_enemy_cards_is_smaller(cards7_enemy, our_cards_value):
		"""this function should be run in parallel but I just can't find a way to do that yet - please help"""
		enemy_cards_value = value_of_best_hand_type_from_seven_cards(cards7_enemy)
		return our_cards_value >= enemy_cards_value

	win = 0

	for table_addition in combinations(deck, 5-len(_table)):
		full_table = _table + table_addition
		rest_of_deck = tuple(deck - set(table_addition))

		our_seven_cards = tuple(sorted(full_table + _hand))

		our_cards_value = value_of_best_hand_type_from_seven_cards(our_seven_cards)

		for enemy_cards in combinations(rest_of_deck, 2):
			# here the code could be set to run on multiple cores to calculate values for different enemy cards
			enemy_seven_cards = tuple(sorted(full_table + enemy_cards))
			win += value_of_enemy_cards_is_smaller(enemy_seven_cards, our_cards_value)

	return round(win * 100 / positions_to_calculate(), 2)


def there_is_con_len5_in_cards7(card_numbers):
	len_cards = len(card_numbers)
	len_loop = len_cards - 5
	for i in range(len_loop + 1):
		cards5 = card_numbers[len_loop - i: len_cards - i]
		f_of_l = cards5[0]
		consecutive_len5 = list(range(f_of_l, f_of_l + 5))
		if cards5 == consecutive_len5:
			return consecutive_len5


def check_if_same_suite_in_cards(cards7):
	colors = [col for _, col in cards7]
	set_of_colors = set(colors)
	for color in set_of_colors:
		count = colors.count(color)
		if count >= 5:
			nums = (num for num, col in cards7[::-1] if col == color)
			max_of_nums = next(nums)
			return max_of_nums


def check_if_same_suite_in_cards_with_numbers(cards7, nums):
	set_of_nums = set(nums)
	colors = [col for num, col in cards7 if num in set_of_nums]
	set_of_cols = set(colors)
	for col in set_of_cols:
		count = colors.count(col)
		if count >= 5:
			return True


@memo
def value_of_best_hand_type_from_seven_cards(cards7):
	"""
	finds best hand type in a set of seven cards player can have - two from player ows and five community cards
	returns integer value to best type of hand found
	"""
	l_of_nums = [num for num, _ in cards7]
	set_of_nums = set(l_of_nums)

	# if there is an ase we want to include its both forms as int: 1 and 14
	if 14 in set_of_nums:
		set_of_nums.add(1)

	numbers = sorted(set_of_nums)
	high_card = numbers[-1]

	# init helper variables
	pair, two_pair, three_of_a_kind, straight, flush, full_house, four_of_a_kind, straight_flush = range(1, 9)
	hand_types_on_table = [False] * 9
	hand_types_on_table[0] = True
	value_of_type = [0] * 9

	def update_hand_type_on_table(hand_type_index, value_of_hand_type):
		nonlocal hand_types_on_table, value_of_type
		hand_types_on_table[hand_type_index] = True
		value_of_type[hand_type_index] = value_of_hand_type

	# check if straight_flush or straight
	consecutive_5_cards_in_cards7 = there_is_con_len5_in_cards7(numbers)
	if consecutive_5_cards_in_cards7:
		max_of_con5 = consecutive_5_cards_in_cards7[-1]
		if check_if_same_suite_in_cards_with_numbers(cards7, consecutive_5_cards_in_cards7):
			return straight_flush * 10000 + max_of_con5 * 100
		else:
			update_hand_type_on_table(straight, max_of_con5)

	# check for flush
	color_on_table = check_if_same_suite_in_cards(cards7)
	if color_on_table:
		update_hand_type_on_table(flush, color_on_table)

	# check for pair, two-pais, full_house, three_of_a_kind etc.
	for number in numbers:
		count = l_of_nums.count(number)

		if count == 4:
			return four_of_a_kind * 10000 + number * 100 + high_card

		elif count == 3:
			if hand_types_on_table[pair]:
				update_hand_type_on_table(full_house, number * 3 + value_of_type[pair] * 2)
			elif hand_types_on_table[three_of_a_kind]:
				other_three = value_of_type[three_of_a_kind]
				update_hand_type_on_table(full_house, max(other_three, number) * 3 + min(other_three, number) * 2)
			else:
				update_hand_type_on_table(three_of_a_kind, number)

		elif count == 2:
			if hand_types_on_table[two_pair]:
				first_pair = value_of_type[pair]
				both_pairs = value_of_type[two_pair]
				second_pair = both_pairs-first_pair
				a = number + first_pair
				b = number + second_pair
				update_hand_type_on_table(two_pair, max(a, b, both_pairs))
			elif hand_types_on_table[full_house]:
				other_two = value_of_type[pair]
				new_value = value_of_type[full_house] + (max(number, other_two) - other_two) * 2
				update_hand_type_on_table(full_house, new_value)
			elif hand_types_on_table[pair]:
				update_hand_type_on_table(two_pair, value_of_type[pair] + number)
			elif hand_types_on_table[three_of_a_kind]:
				update_hand_type_on_table(full_house, value_of_type[three_of_a_kind] * 3 + number * 2)
			else:
				update_hand_type_on_table(pair, number)

	for i in range(9):
		current_index = 8-i
		if hand_types_on_table[current_index]:
			count_highest_card = current_index not in {straight, flush, full_house, straight_flush}
			return 10000 * current_index + 100 * value_of_type[current_index] + high_card * count_highest_card


if __name__ == '__main__':
	from cProfile import run
	hand = {('A', 'h'), ('A', 's')}
	base = {('3', 'h'), ('3', 's'), ('A', 'c')}

	set_table_as(base)
	update_hand(hand)
	result = calculate_position
	run('result()', sort='cumtime')
