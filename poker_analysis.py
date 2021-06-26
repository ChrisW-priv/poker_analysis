from itertools import combinations
from cProfile import run


class PokerEvaluator:
	def __init__(self):
		self._table = set()
		self._hand = set()
		self.HAND_VALUES = ['highest_card', 'para', 'dwie_pary', 'trojka', 'strit', 'kolor', 'full', 'kareta', 'poker']
		self.COLOURS = ['h', 'c', 'd', 's']
		self.CARD_VALUES = {
			'J': 11,
			'D': 12,
			'K': 13,
			'A': 14,
			**{str(n): n for n in range(2, 11)}
		}
		self.deck = set((card, colour) for card in self.CARD_VALUES for colour in self.COLOURS)

	def reset_deck(self):
		self.deck = set((card, colour) for card in self.CARD_VALUES for colour in self.COLOURS)

	def reset_table(self, table):
		self._table = table

	def update_table(self, card):
		self._table.update(card)

	def update_hand(self, hand):
		self._hand = hand

	def calculate_position(self):
		"""we have the hand and incomplete table and the hand of most powerful enemy"""
		self.deck -= self._hand
		self.deck -= self._table

		win = 0
		draw = 0
		loss = 0

		for table_addition in combinations(self.deck, 5-len(self._table)):
			full_table = self._table.union(table_addition)
			our_cards_value = self.value_of_players_hand(full_table, self._hand)

			rest_of_deck = self.deck - set(table_addition)
			for enemy_cards in combinations(rest_of_deck, 2):
				enemy_cards_value = self.value_of_players_hand(full_table, enemy_cards)
				if our_cards_value > enemy_cards_value:
					win += 1
				elif our_cards_value == enemy_cards_value:
					draw += 1
				else:
					loss += 1

		return win, draw, loss

	def value_of_players_hand(self, base, hand):
		both_combined = base.union(hand)
		hand_type, val, highest_card = self.best_hand_type_from_seven_cards(both_combined)
		# hand type is an int representing index of type
		# if hand type is strit, kolor, full or poker we do not add the highest card
		count_highest_card = hand_type not in {4, 5, 6, 8}
		return 1000 * hand_type + 10 * val + highest_card * count_highest_card

	def best_hand_type_from_seven_cards(self, cards7):
		def check_consecutive_len5(cards5):
			"""checks if ordered cards are incrementing by one"""
			sorted_l = sorted(cards5)
			consecutive_len5 = list(range(sorted_l[0], sorted_l[0] + 6))
			return sorted_l == consecutive_len5

		def check_if_colour_in_cards(cards):
			colours = (colour for _, colour in cards)
			for colour in self.COLOURS:
				c = sum(colour == col for col in colours)
				if c == 5:
					return True

		# we make a list of all cards as numbers based on their value
		numbers = [self.CARD_VALUES[number] for number, _ in cards7]
		highest_card = max(numbers)

		para, dwie_pary, trojka, strit, kolor, full, kareta, poker = range(1, 9)  # indexes of hand types
		hand_types_on_table = [False for _ in self.HAND_VALUES]
		hand_types_on_table[0] = True
		value_of_type = [0 for _ in self.HAND_VALUES]

		def update_hand_type_on_table(hand_type_index, value_of_hand_type):
			nonlocal hand_types_on_table, value_of_type
			hand_types_on_table[hand_type_index] = True
			value_of_type[hand_type_index] = max(value_of_hand_type, value_of_type[hand_type_index])

		# check if poker or strit
		for combination_of5 in combinations(cards7, 5):
			main = [self.CARD_VALUES[number] for number, _ in combination_of5]
			max_main = max(main)

			# if there is an ase we have to look for two separate cases
			secondary = [] if 14 not in main else [1 if x == 14 else x for x in main]

			if check_if_colour_in_cards(combination_of5):
				update_hand_type_on_table(kolor, max_main)
				if check_consecutive_len5(main):
					update_hand_type_on_table(poker, max_main)
				elif secondary and check_consecutive_len5(secondary):
					update_hand_type_on_table(poker, max(secondary))
			else:
				if check_consecutive_len5(main):
					update_hand_type_on_table(strit, max_main)
				elif secondary and check_consecutive_len5(secondary):
					update_hand_type_on_table(strit, max(secondary))

		for number in set(numbers):
			count = numbers.count(number)

			if count == 4:
				update_hand_type_on_table(kareta, number)

			elif count == 3:
				# if "para" on the table
				if hand_types_on_table[para]:
					update_hand_type_on_table(full, number * 3 + value_of_type[para] * 2)
				# if "trójka" on the table
				elif hand_types_on_table[trojka]:
					other_three = value_of_type[trojka]
					update_hand_type_on_table(full, max(other_three, number) * 3 + min(other_three, number) * 2)
				else:
					update_hand_type_on_table(trojka, number)

			elif count == 2:
				# if "para" on the table
				if hand_types_on_table[para]:
					update_hand_type_on_table(dwie_pary, value_of_type[para] + number)
				# if "trójka" on the table
				elif hand_types_on_table[trojka]:
					update_hand_type_on_table(full, value_of_type[trojka] * 3 + number * 2)
				else:
					update_hand_type_on_table(para, number)

		len_hand_values = len(self.HAND_VALUES)
		for i in range(len_hand_values):
			current_index = len_hand_values-i-1
			if hand_types_on_table[current_index]:
				return current_index, value_of_type[current_index], highest_card


if __name__ == '__main__':
	hand = {('A', 'h'), ('A', 's')}
	base = {('3', 'h'), ('3', 's'), ('3', 'd'), ('A', 'c'), ('A', 'd')}

	evaluator = PokerEvaluator()
	evaluator.update_table(base)
	evaluator.update_hand(hand)
	result = evaluator.calculate_position
	run('result()', sort='cumtime')
