from collections import Counter
from itertools import combinations


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
			deck = self.deck - set(table_addition)
			our_cards_value = self.max_value_of_players_hand(full_table, self._hand)
			for enemy_cards in combinations(deck, 2):
				enemy_cards_value = self.max_value_of_players_hand(full_table, enemy_cards)
				if our_cards_value > enemy_cards_value:
					win += 1
				elif our_cards_value == enemy_cards_value:
					draw += 1
				else:
					loss += 1
					print(enemy_cards, our_cards_value, enemy_cards_value)

		print(win, draw, loss)

	def max_value_of_players_hand(self, base, hand):
		both_combined = base.union(hand)
		max_ = 0

		for cards in combinations(both_combined, 5):
			val = self.value_of_five_cards(cards)
			max_ = max(max_, val)

		return max_

	def get_hand_type_of_five_cards(self, cards):
		def check_consecutive_len5(l):
			"""checks if ordered cards are incrementing by one"""
			what_it_would_be = list(range(min(l), max(l) + 1))
			return sorted(l) == what_it_would_be and len(what_it_would_be) == 5

		# we make a list of all cards as numbers based on their value
		main = [self.CARD_VALUES[number] for number, _ in cards]
		# if there is an ase we have to look for two separate cases
		secondary = [] if 14 not in main else [1 if x == 14 else x for x in main]

		highest_card = max(main)

		# we check if there are five cards of the same colour
		colours_on_table = (colours for _, colours in cards)
		there_is_colour_of_type = (all(col == colour for col in colours_on_table) for colour in self.COLOURS)
		colour_on_table = any(there_is_colour_of_type)

		"""We check if there is strit or poker on table"""
		if check_consecutive_len5(main):
			if colour_on_table:
				return 'poker', highest_card, highest_card
			else:
				return 'strit', highest_card, highest_card
		if secondary:
			"""we need to check if there is strit or poker on table provided we count the ase as 1 (if ase on table)"""
			if check_consecutive_len5(secondary):
				if colour_on_table:
					return 'poker', max(secondary), highest_card
				else:
					return 'strit', max(secondary), highest_card

		"""if there are 5 cards of the same colour and method has not terminated by this point 
		we return 'colour' as the highest type of hand one can have'"""
		if colour_on_table:
			return 'kolor', highest_card, highest_card

		type_of_hand = 'highest_card'
		value_of_hand = 0

		for number in main:
			count = main.count(number)

			if count == 2:
				if type_of_hand == 'para':
					return 'dwie_pary', value_of_hand + number, highest_card
				elif type_of_hand == 'trojka':
					return 'full', value_of_hand * 3 + number * 2, highest_card
				else:
					type_of_hand = 'para'
					value_of_hand = number

			elif count == 3:
				if type_of_hand == 'para':
					return 'full', value_of_hand * 2 + number * 3, highest_card
				else:
					type_of_hand = 'trojka'
					value_of_hand = number

			elif count == 4:
				return 'kareta', number, highest_card

		return type_of_hand, value_of_hand, highest_card

	def value_of_five_cards(self, cards):
		"""finds type of hand, value of it and highest card player has based on five cards passed as 'cards'. """
		"""returns value of those five cards based on the evaluation by self.value_of_hand_type method"""

		def check_consecutive_len5(l):
			"""checks if ordered cards are incrementing by one"""
			what_it_would_be = list(range(min(l), max(l) + 1))
			return sorted(l) == what_it_would_be and len(what_it_would_be) == 5

		# we make a list of all cards as numbers based on their value
		main = [self.CARD_VALUES[number] for number, _ in cards]
		# if there is an ase we have to look for two separate cases
		secondary = [] if 14 not in main else [1 if x == 14 else x for x in main]

		highest_card = max(main)

		# we check if there are five cards of the same colour
		colours_on_table = (colours for _, colours in cards)
		there_is_colour_of_type = (all(col == colour for col in colours_on_table) for colour in self.COLOURS)
		colour_on_table = any(there_is_colour_of_type)

		"""We check if there is strit or poker on table"""
		if check_consecutive_len5(main):
			if colour_on_table:
				return self.value_of_hand_type('poker', highest_card)
			else:
				return self.value_of_hand_type('strit', highest_card)
		if secondary:
			"""we need to check if there is strit or poker on table provided we count the ase as 1 (if ase on table)"""
			if check_consecutive_len5(secondary):
				if colour_on_table:
					return self.value_of_hand_type('poker', max(secondary))
				else:
					return self.value_of_hand_type('strit', max(secondary))

		"""if there are 5 cards of the same colour and method has not terminated by this point 
		we return 'colour' as the highest type of hand one can have'"""
		if colour_on_table:
			return self.value_of_hand_type('kolor', highest_card, highest_card)

		type_of_hand = 'highest_card'
		value_of_hand = 0

		for number in main:
			count = main.count(number)

			if count == 2:
				if type_of_hand == 'para':
					return self.value_of_hand_type('dwie_pary', value_of_hand * 2 + number * 2, highest_card)
				elif type_of_hand == 'trojka':
					return self.value_of_hand_type('full', value_of_hand * 3 + number * 2, highest_card)
				else:
					type_of_hand = 'para'
					value_of_hand = number

			elif count == 3:
				if type_of_hand == 'para':
					return self.value_of_hand_type('full', value_of_hand * 2 + number * 3, highest_card)
				else:
					type_of_hand = 'trojka'
					value_of_hand = number

			elif count == 4:
				return self.value_of_hand_type('kareta', number, highest_card)

		return self.value_of_hand_type(type_of_hand, value_of_hand, highest_card)

	def value_of_hand_type(self, hand_type, value_of_hand_type, max_card=0):
		"""based on th type of hand this method gives a value of that"""
		if hand_type != 'highest_card':
			return 1000 * self.HAND_VALUES.index(hand_type) + 10 * value_of_hand_type + max_card
		else:
			return max_card


if __name__ == '__main__':
	hand = {('A', 'h'), ('A', 's')}
	base = {('3', 'h'), ('3', 's'), ('3', 'd'), ('A', 'd'), ('A', 'c')}

	evaluator = PokerEvaluator()
	evaluator.update_table(base)
	evaluator.update_hand(hand)
	evaluator.calculate_position()
