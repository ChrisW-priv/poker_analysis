from itertools import combinations

# types of hand:
# 'highest_card','pair','two_pair','three_of_a_kind','straight','flush','full_house','four_of_a_kind','straight_flush'
# card suites:
# diamonds (♦), clubs (♣), hearts (♥) and spades (♠)


cdef dict memo_table = {}


cdef class PokerEvaluator:
	SUITES = ('d', 'c', 'h', 's')
	CARD_VALUES = {'J': 11, 'D': 12, 'K': 13, 'A': 14, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10}

	cdef set deck
	cdef tuple _hand, _table

	def __init__(self):
		self._table = tuple()
		self._hand = tuple()
		self.deck = set()

		self.reset_deck()

	def reset_deck(self):
		self.deck = set(PokerEvaluator._normalize_card((num, col)) for num in PokerEvaluator.CARD_VALUES for col in PokerEvaluator.SUITES)

	@staticmethod
	def _normalize_card(card):
		"""takes a tuple (str, str) and normalises it to make it consistent across code, returns (int, int) tuple"""
		number = PokerEvaluator.CARD_VALUES[card[0]]
		color = PokerEvaluator.SUITES.index(card[1])
		return number, color

	def set_table_as(self, table):
		"""resets table of community cards to given set of cards"""
		table = set(PokerEvaluator._normalize_card(card) for card in table)
		self._table = tuple(table)
		self.deck -= table

	def update_table(self, card):
		"""adds normalised card to a table of community cards"""
		card = PokerEvaluator._normalize_card(card)
		self._table + card
		self.deck -= card

	def update_hand(self, players_hand):
		"""normalises cards and sets them as current cards of a player"""
		players_hand = set(PokerEvaluator._normalize_card(card) for card in players_hand)
		self._hand = tuple(players_hand)
		self.deck -= players_hand

	cdef int positions_to_calculate(self):
		"""calculates how many positions are there to consider during evaluation"""
		"""returns number of possible combinations of full table times number of combinations for enemy cards"""

		n_cards_left_in_deck = len(self.deck)
		n_cards_left_to_full_table = 5 - len(self._table)
		cdef int multiplier = 1
		cdef int denominator = 1
		for i in range(n_cards_left_to_full_table):
			multiplier *= (n_cards_left_in_deck - i)
			denominator *= (i+1)

		cards_to_choose_from_for_enemy = n_cards_left_in_deck - n_cards_left_to_full_table
		for i in range(2):
			multiplier *= (cards_to_choose_from_for_enemy - i)
			denominator *= (i+1)

		return multiplier//denominator

	cpdef double calculate_position(self):
		"""calculates percentage of how many times we win or make a draw compered to all position that we consider"""

		cdef int win = 0
		cdef int our_cards_value, enemy_cards_value
		cdef tuple full_table, rest_of_deck, our_seven_cards, enemy_seven_cards

		for table_addition in combinations(self.deck, 5-len(self._table)):
			full_table = self._table + table_addition
			rest_of_deck = tuple(self.deck - set(table_addition))

			our_seven_cards = tuple(sorted(full_table + self._hand))

			our_cards_value = PokerEvaluator.value_of_best_hand_type_from_seven_cards(our_seven_cards)

			for enemy_cards in combinations(rest_of_deck, 2):
				# here the code could be set to run on multiple cores to calculate values for different enemy cards
				enemy_seven_cards = tuple(sorted(full_table + enemy_cards))
				enemy_cards_value = PokerEvaluator.memoized_value_of_best_hand_type_from_seven_cards(enemy_seven_cards)
				win += (our_cards_value >= enemy_cards_value)

		return round(win * 100 / self.positions_to_calculate(), 2)

	@staticmethod
	cdef int memoized_value_of_best_hand_type_from_seven_cards(tuple cards7):
		if cards7 in memo_table:
			return memo_table[cards7]

		cdef int val = PokerEvaluator.value_of_best_hand_type_from_seven_cards(cards7)
		memo_table[cards7] = val
		return val

	@staticmethod
	cdef int value_of_best_hand_type_from_seven_cards(tuple cards7):
		"""
		finds best hand type in a set of seven cards player can have - two from player ows and five community cards
		returns integer value to best type of hand found
		"""
		cdef list l_of_nums, numbers,hand_types_on_table, value_of_type

		l_of_nums = [num for num, _ in cards7]
		cdef set set_of_nums = set(l_of_nums)

		# if there is an ase we want to include its both forms as int: 1 and 14
		if 14 in set_of_nums:
			set_of_nums.add(1)

		numbers = sorted(set_of_nums)
		cdef int high_card = numbers[-1]

		# init helper variables
		cdef int pair = 1
		cdef int two_pair = 2
		cdef int three_of_a_kind = 3
		cdef int straight = 4
		cdef int flush = 5
		cdef int full_house = 6
		cdef int four_of_a_kind = 7
		cdef int straight_flush = 8
		hand_types_on_table = [False for _ in range(9)]
		hand_types_on_table[0] = True
		value_of_type = [0 for _ in range(9)]

		def update_hand_type_on_table(int hand_type_index, int value_of_hand_type):
			nonlocal hand_types_on_table, value_of_type
			hand_types_on_table[hand_type_index] = True
			value_of_type[hand_type_index] = value_of_hand_type

		# check if straight_flush or straight
		cdef list consecutive_5_cards_in_cards7 = PokerEvaluator._there_is_con_len5_in_cards7(numbers)
		cdef int max_of_con5
		if consecutive_5_cards_in_cards7:
			max_of_con5 = consecutive_5_cards_in_cards7[-1]
			if PokerEvaluator._check_if_same_suite_in_cards_with_numbers(cards7, consecutive_5_cards_in_cards7):
				return straight_flush * 10000 + max_of_con5 * 100
			else:
				update_hand_type_on_table(straight, max_of_con5)

		# check for flush
		cdef int color_on_table = PokerEvaluator._check_if_same_suite_in_cards(cards7)
		if color_on_table:
			update_hand_type_on_table(flush, color_on_table)

		# check for pair, two-pais, full_house, three_of_a_kind etc.
		cdef int num_count, first_pair, both_pairs, second_pair, a, b, other_two, new_value
		for number in numbers:
			num_count = l_of_nums.count(number)

			if num_count == 4:
				return four_of_a_kind * 10000 + number * 100 + high_card

			elif num_count == 3:
				if hand_types_on_table[pair]:
					update_hand_type_on_table(full_house, number * 3 + value_of_type[pair] * 2)
				elif hand_types_on_table[three_of_a_kind]:
					other_three = value_of_type[three_of_a_kind]
					update_hand_type_on_table(full_house, max(other_three, number) * 3 + min(other_three, number) * 2)
				else:
					update_hand_type_on_table(three_of_a_kind, number)

			elif num_count == 2:
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

	@staticmethod
	cdef list _there_is_con_len5_in_cards7(list card_numbers):
		cdef int len_cards, len_loop, f_of_l
		cdef list cards5, consecutive_len5
		len_cards = len(card_numbers)
		len_loop = len_cards - 5
		for i in range(len_loop + 1):
			cards5 = card_numbers[len_loop - i: len_cards - i]
			f_of_l = cards5[0]
			consecutive_len5 = list(range(f_of_l, f_of_l + 5))
			if cards5 == consecutive_len5:
				return consecutive_len5

	@staticmethod
	cdef int _check_if_same_suite_in_cards(tuple cards7):
		cdef list colors = [col for _, col in cards7]
		cdef set set_of_colors = set(colors)
		cdef int num_count, max_of_nums
		for color in set_of_colors:
			num_count = colors.count(color)
			if num_count >= 5:
				nums = (num for num, col in cards7[::-1] if col == color)
				max_of_nums = next(nums)
				return max_of_nums

	@staticmethod
	cdef int _check_if_same_suite_in_cards_with_numbers(tuple cards7, list nums):
		cdef set set_of_nums = set(nums)
		cdef list colors = [col for num, col in cards7 if num in set_of_nums]
		cdef set set_of_cols = set(colors)
		cdef int col_count, col
		for col in set_of_cols:
			col_count = colors.count(col)
			if col_count >= 5:
				return True
