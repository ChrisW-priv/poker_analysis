from collections import Counter


class PokerEvaluator:
	def __init__(self, hand=None):
		self._hand = [('A', 'h'), ('A', 's')] if not hand else hand
		self.COLOURS = ['h', 'c', 'd', 's']
		self.HAND_VALUES = ['highest_card', 'para', 'dwie_pary', 'trojka', 'strit', 'kolor', 'full', 'kareta', 'poker']
		self.CARD_VALUES = {
			'J': 11,
			'D': 12,
			'K': 13,
			'A': 14,
			**{str(n): n for n in range(2, 11)}
		}

	def update_hand(self, hand):
		self._hand = hand

	def find_hand_type(self, cards):
		def check_consecutive(l):
			return sorted(l) == list(range(min(l), max(l) + 1))

		# counter helps with counting pairs, triples, colours etc.
		table = Counter()

		# if there is an ase we have to look for two separate cases
		main = []
		for card in cards:
			number, colour = card
			table[self.CARD_VALUES[number]] += 1
			table[colour] += 1
			main.append(self.CARD_VALUES[number])

		secondary = [] if 14 not in main else [n for n in main if n != 14] + [1]

		type_of_hand = {}

		def update_hand(key, value):
			nonlocal type_of_hand
			type_of_hand = {key: {'value': value}}

		for colour in self.COLOURS:
			if table[colour] == 5: update_hand('kolor', max(main))

		if check_consecutive(main):
			update_hand('strit', max(main))
			for colour in self.COLOURS:
				if table[colour] == 5: update_hand('poker', max(main))
		if secondary:
			if check_consecutive(secondary):
				update_hand('strit', max(secondary))
				for colour in self.COLOURS:
					if table[colour] == 5: update_hand('poker', max(secondary))

		for number in self.CARD_VALUES:
			count = table[self.CARD_VALUES.get(number)]

			if count == 2:
				if type_of_hand.get('para'):
					update_hand('dwie_pary', type_of_hand.get('para').get('value')*2 + self.CARD_VALUES[number]*2)
				elif type_of_hand.get('trojka'):
					update_hand('full', type_of_hand.get('trojka').get('value')*3 + self.CARD_VALUES[number]*2)
				else:
					update_hand('para', self.CARD_VALUES[number])

			if count == 3:
				if type_of_hand.get('para'):
					update_hand('full', type_of_hand.get('para').get('value')*2 + self.CARD_VALUES[number]*3)
				else:
					update_hand('trojka', self.CARD_VALUES[number])

			if count == 4: update_hand('kareta', self.CARD_VALUES[number])

		type_of_hand['highest_card'] = max(main)
		return type_of_hand

	def best_type_player_has(self, hand, base):
		from itertools import combinations
		hand_type_of_best_combination = {}
		max_value = 0
		for combination in combinations(base + hand, 5):
			hand_type = self.find_hand_type(combination)
			value = self.value_of_hand_type(hand_type)

			if value > max_value:
				max_value = value
				hand_type_of_best_combination = hand_type

		return hand_type_of_best_combination

	def value_of_hand_type(self, hand_type):
		value = 0
		for key in hand_type:
			if key in ['para', 'dwie_pary', 'trojka', 'kolor', 'kareta']:
				value = 1000 * self.HAND_VALUES.index(key) + 10 * hand_type.get(key).get('value') + hand_type['highest_card']
				break
			elif key in ['strit', 'full', 'poker']:
				value = 1000 * self.HAND_VALUES.index(key) + 10 * hand_type.get(key).get('value')
				break
			else:
				value = hand_type['highest_card']

		return value


if __name__ == '__main__':
	evaluator = PokerEvaluator()
	hand = [('2', 'h'), ('2', 's')]
	base = [('3', 'h'), ('3', 's'), ('3', 'd'), ('A', 's'), ('A', 'h')]

	c = evaluator.best_type_player_has(hand, base)
	print(c)
