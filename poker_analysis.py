from itertools import combinations

# types of hand:
# 'highest_card','pair','two_pair','three_of_a_kind','straight','flush','full_house','four_of_a_kind','straight_flush'
# card suites:
# diamonds (♦), clubs (♣), hearts (♥) and spades (♠)


class PokerEvaluator:
	SUITES = ('d', 'c', 'h', 's')
	CARD_VALUES = {
		'J': 11,
		'D': 12,
		'K': 13,
		'A': 14,
		**{str(n): n for n in range(2, 11)}
	}

	def __init__(self):
		self._table = set()
		self._hand = set()
		self.deck = set()

		self.reset_deck()

	def reset_deck(self):
		self.deck = set(self.normalize_card((num, col)) for num in self.CARD_VALUES for col in self.SUITES)

	@staticmethod
	def normalize_card(card):
		"""takes a tuple (str, str) and normalises it to make it consistent across code, returns (int, int) tuple"""
		number = PokerEvaluator.CARD_VALUES[card[0]]
		color = PokerEvaluator.SUITES.index(card[1])
		return number, color

	def set_table_as(self, table: set):
		"""resets table of community cards to given set of cards"""
		table = set(PokerEvaluator.normalize_card(card) for card in table)
		self._table = table
		self.deck -= table

	def update_table(self, card):
		"""adds normalised card to a table of community cards"""
		card = PokerEvaluator.normalize_card(card)
		self._table.update(card)
		self.deck -= card

	def update_hand(self, players_hand):
		"""normalises cards and sets them as current cards of a player"""
		players_hand = set(PokerEvaluator.normalize_card(card) for card in players_hand)
		self._hand = players_hand
		self.deck -= players_hand

	@property
	def positions_to_calculate(self):
		"""calculates how many positions are there to consider during evaluation"""
		n_cards_left_in_deck = len(self.deck)
		n_cards_left_to_full_table = 5 - len(self._table)
		n = 1
		for i in range(n_cards_left_to_full_table):
			n *= (n_cards_left_in_deck - i)
			n /= (i+1)

		cards_to_choose_from_for_enemy = n_cards_left_in_deck - n_cards_left_to_full_table
		for i in range(2):
			n *= (cards_to_choose_from_for_enemy - i)
			n /= (i+1)

		return int(n)

	def calculate_position(self):
		"""calculates percentage of how many times we win or make a draw compered to all position that we consider"""

		def value_of_enemy_cards_is_smaller(cards7_enemy, our_cards_value):
			"""this function should be run in parallel but I just can't find a way to do that yet - please help"""
			enemy_cards_value = PokerEvaluator.value_of_best_hand_type_from_seven_cards(cards7_enemy)
			return our_cards_value >= enemy_cards_value

		win = 0

		for table_addition in combinations(self.deck, 5-len(self._table)):
			full_table = self._table.union(table_addition)
			rest_of_deck = self.deck - set(table_addition)

			our_seven_cards = full_table.union(self._hand)

			our_cards_value = PokerEvaluator.value_of_best_hand_type_from_seven_cards(our_seven_cards)

			for enemy_cards in combinations(rest_of_deck, 2):
				# here the code could be set to run on multiple cores to calculate values for different enemy cards
				enemy_seven_cards = full_table.union(enemy_cards)
				win += value_of_enemy_cards_is_smaller(enemy_seven_cards, our_cards_value)

		return round(win * 100 / self.positions_to_calculate, 2)

	@staticmethod
	def value_of_best_hand_type_from_seven_cards(cards7):
		"""
		finds best hand type in a set of seven cards player can have - two from player ows and five community cards
		returns integer value to best type of hand found
		"""

		numbers = sorted(set([number for number, _ in cards7]))

		# init helper variables
		pair, two_pair, three_of_a_kind, straight, flush, full_house, four_of_a_kind, straight_flush = range(1, 9)
		hand_types_on_table = [False for _ in range(9)]
		hand_types_on_table[0] = True
		value_of_type = [0 for _ in range(9)]

		def update_hand_type_on_table(hand_type_index, value_of_hand_type):
			nonlocal hand_types_on_table, value_of_type
			hand_types_on_table[hand_type_index] = True
			value_of_type[hand_type_index] = value_of_hand_type

		# check if straight_flush or straight
		consecutive_5_cards_in_cards7 = PokerEvaluator.there_is_con_len5_in_cards7(numbers)
		if consecutive_5_cards_in_cards7:
			max_of_con5 = max(consecutive_5_cards_in_cards7)
			if PokerEvaluator.check_if_same_suite_in_cards_with_numbers(cards7, consecutive_5_cards_in_cards7):
				update_hand_type_on_table(straight_flush, max_of_con5)
			else:
				update_hand_type_on_table(straight, max_of_con5)

		# check for flush
		color_on_table = PokerEvaluator.check_if_same_suite_in_cards(cards7)
		if color_on_table:
			update_hand_type_on_table(flush, max(color_on_table))

		# check for pair, two-pais, full_house, three_of_a_kind etc.
		for number in numbers:
			count = sum(num == number for num, _ in cards7)

			if count == 4:
				update_hand_type_on_table(four_of_a_kind, number)

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
				return 10000 * current_index + 100 * value_of_type[current_index] + numbers[-1] * count_highest_card

	@staticmethod
	def there_is_con_len5_in_cards7(cards):
		len_cards = len(cards)
		len_loop = len_cards - 5
		for i in range(len_loop + 1):
			cards5 = cards[len_loop - i: len_cards - i]
			f_of_l = cards5[0]
			consecutive_len5 = list(range(f_of_l, f_of_l + 5))
			if cards5 == consecutive_len5:
				return cards5

	@staticmethod
	def check_if_same_suite_in_cards(cards7):
		colors = [col for _, col in cards7]
		set_of_colors = set(colors)
		for color in set_of_colors:
			count = colors.count(color)
			if count == 5:
				nums = (num for num, col in cards7 if col == color)
				return nums

	@staticmethod
	def check_if_same_suite_in_cards_with_numbers(cards7, nums):
		set_of_nums = set(nums)
		colors = [col for num, col in cards7 if num in set_of_nums]
		set_of_cols = set(colors)
		for col in set_of_cols:
			count = colors.count(col)
			if count == 5:
				return True


if __name__ == '__main__':
	from cProfile import run
	hand = {('A', 'h'), ('A', 's')}
	base = {('3', 'h'), ('3', 's'), ('3', 'd'), ('A', 'c')}

	evaluator = PokerEvaluator()
	evaluator.set_table_as(base)
	evaluator.update_hand(hand)
	result = evaluator.calculate_position
	run('result()', sort='cumtime')
