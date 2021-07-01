from itertools import combinations
from cProfile import run


class PokerEvaluator:
	COLOURS = ('h', 'c', 'd', 's')
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

		self.HAND_VALUES = ['highest_card', 'para', 'dwie_pary', 'trojka', 'strit', 'kolor', 'full', 'kareta', 'poker']
		self.reset_deck()

	def reset_deck(self):
		self.deck = set(self.normalize_card((num, col)) for num in self.CARD_VALUES for col in self.COLOURS)

	@staticmethod
	def normalize_card(card):
		number = PokerEvaluator.CARD_VALUES[card[0]]
		color = PokerEvaluator.COLOURS.index(card[1])
		return number, color

	def set_table_as(self, table):
		table = set(PokerEvaluator.normalize_card(card) for card in table)
		self._table = table

	def update_table(self, card):
		card = PokerEvaluator.normalize_card(card)
		self._table.update(card)

	def update_hand(self, players_hand):
		players_hand = set(PokerEvaluator.normalize_card(card) for card in players_hand)
		self._hand = players_hand

	def calculate_position(self):
		"""we have the hand and incomplete table and the hand of most powerful enemy"""
		self.deck -= self._hand
		self.deck -= self._table

		win = 0
		draw = 0
		loss = 0

		for table_addition in combinations(self.deck, 5-len(self._table)):
			full_table = self._table.union(table_addition)
			rest_of_deck = self.deck - set(table_addition)

			our_hand_type, our_val, our_highest_card = self.best_hand_type_from_seven_cards(full_table.union(self._hand))
			our_cards_value = self.value_of_players_hand(our_hand_type, our_val, our_highest_card)

			for enemy_cards in combinations(rest_of_deck, 2):
				enemy_hand_type, enemy_val, enemy_highest_card = self.best_hand_type_from_seven_cards(full_table.union(enemy_cards))
				enemy_cards_value = self.value_of_players_hand(enemy_hand_type, enemy_val, enemy_highest_card)
				if our_cards_value > enemy_cards_value:
					win += 1
				elif our_cards_value == enemy_cards_value:
					draw += 1
				else:
					loss += 1

		return win, draw, loss

	def best_hand_type_from_seven_cards(self, cards7):
		# we make a list of all cards as numbers based on their value
		numbers = sorted(set([number for number, _ in cards7]))
		highest_card = max(numbers)

		# init helper variables
		para, dwie_pary, trojka, strit, kolor, full, kareta, poker = range(1, 9)  # indexes of hand types
		hand_types_on_table = [False for _ in self.HAND_VALUES]
		hand_types_on_table[0] = True
		value_of_type = [0 for _ in self.HAND_VALUES]

		def update_hand_type_on_table(hand_type_index, value_of_hand_type):
			nonlocal hand_types_on_table, value_of_type
			hand_types_on_table[hand_type_index] = True
			value_of_type[hand_type_index] = value_of_hand_type

		# check if poker or strit
		consecutive_5_cards_in_cards7 = PokerEvaluator.there_is_con_len5_in_cards7(numbers)
		if consecutive_5_cards_in_cards7:
			max_of_con5 = max(consecutive_5_cards_in_cards7)
			if PokerEvaluator.check_if_color_in_cards_with_numbers(cards7, consecutive_5_cards_in_cards7):
				update_hand_type_on_table(poker, max_of_con5)
			else:
				update_hand_type_on_table(strit, max_of_con5)

		# check for kolor
		color_on_table = PokerEvaluator.check_if_color_in_cards(cards7)
		if color_on_table:
			update_hand_type_on_table(kolor, max(color_on_table))

		# check for para, dwie-pary, full, trojka etc.
		for number in numbers:
			count = sum(num == number for num, _ in cards7)

			if count == 4:
				update_hand_type_on_table(kareta, number)

			elif count == 3:
				if hand_types_on_table[para]:
					update_hand_type_on_table(full, number * 3 + value_of_type[para] * 2)
				elif hand_types_on_table[trojka]:
					other_three = value_of_type[trojka]
					update_hand_type_on_table(full, max(other_three, number) * 3 + min(other_three, number) * 2)
				else:
					update_hand_type_on_table(trojka, number)

			elif count == 2:
				if hand_types_on_table[dwie_pary]:
					pierwsza_para = value_of_type[para]
					obie_pary = value_of_type[dwie_pary]
					druga_para = obie_pary-pierwsza_para
					a = number + pierwsza_para
					b = number + druga_para
					update_hand_type_on_table(dwie_pary, max(a, b, obie_pary))
				elif hand_types_on_table[full]:
					other_two = value_of_type[para]
					new_value = value_of_type[full] + (max(number, other_two) - other_two) * 2
					update_hand_type_on_table(full, new_value)
				elif hand_types_on_table[para]:
					update_hand_type_on_table(dwie_pary, value_of_type[para] + number)
				elif hand_types_on_table[trojka]:
					update_hand_type_on_table(full, value_of_type[trojka] * 3 + number * 2)
				else:
					update_hand_type_on_table(para, number)

		len_hand_values = len(self.HAND_VALUES)
		for i in range(len_hand_values):
			current_index = len_hand_values-i-1
			if hand_types_on_table[current_index]:
				return current_index, value_of_type[current_index], highest_card

	@staticmethod
	def value_of_players_hand(hand_type, val, highest_card):
		# if hand type is strit, kolor, full or poker we do not add the highest card
		count_highest_card = hand_type not in {4, 5, 6, 8}
		return 10000 * hand_type + 100 * val + highest_card * count_highest_card

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
	def check_if_color_in_cards(cards7):
		colors = [col for _, col in cards7]
		set_of_colors = set(colors)
		for color in set_of_colors:
			count = colors.count(color)
			if count == 5:
				nums = (num for num, col in cards7 if col == color)
				return nums

	@staticmethod
	def check_if_color_in_cards_with_numbers(cards7, nums):
		set_of_nums = set(nums)
		colors = [col for num, col in cards7 if num in set_of_nums]
		set_of_cols = set(colors)
		for col in set_of_cols:
			count = colors.count(col)
			if count == 5:
				return True


if __name__ == '__main__':
	hand = {('A', 'h'), ('A', 's')}
	base = {('3', 'h'), ('3', 's'), ('3', 'd'), ('A', 'c')}

	evaluator = PokerEvaluator()
	evaluator.set_table_as(base)
	evaluator.update_hand(hand)
	result = evaluator.calculate_position
	run('result()', sort='cumtime')
