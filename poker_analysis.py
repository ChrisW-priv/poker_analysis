from collections import Counter

# J D K A
# hearts club diamonds spades

cards = [('A', 'h'), ('2', 'h'), ('3', 'h'), ('4', 'd'), ('5', 'c'), ('3', 'c'), ('3', 's')]

numbers = [str(n) for n in range(2, 11)] + ['J', 'D', 'K', 'A']
colours = ['h', 'c', 'd', 's']
table = Counter()

for card in cards:
	number, colour = card
	table[number] += 1
	table[colour] += 1


kombinacje = {
	'para': 0,
	'dwie pary': 0,
	'trojka': 0,
	'kareta': 0,
	'full': 0,
	'kolor': 0
}

for number in numbers:
	count = table[number]
	if count == 2:
		kombinacje['para'] += 1
	if count == 3:
		kombinacje['trojka'] += 1
	if count == 4:
		kombinacje['kareta'] += 1

kombinacje['full'] = 1*(kombinacje['para'] >= 1 and kombinacje['trojka'] >= 1)
kombinacje['dwie pary'] = 1*(kombinacje['para'] >= 2)

for colour in colours:
	if table[colour] >= 5:
		kombinacje['kolor'] = 1
