import pronouncing
import nltk
nltk.download('punkt')
import sys
import random
import string
import enchant
import pandas as pd

def main():
	d = enchant.Dict("en_US")
	text = open(sys.argv[1])
	output = open("output.txt", "w")
	str = text.read()
	out = []
	counter = 0
	rhyme = ""

	word_pool = set()

	# Import a frequency list for 5000 common words
	word_freq_file = 'frequency.xlsx'
	file = pd.ExcelFile(word_freq_file)
	dataframe = file.parse('Sheet1')
	for i in range(4999):
		word_pool.add(dataframe.ix[i, 1].strip())
	print(len(word_pool))

	# To clean punctuation
	translator = str.maketrans('', '', string.punctuation)

	# On each line, we will replace the word with a new word with the same
	# Cadence
	for line in str.splitlines():
		words = line.split()
		tokens = nltk.word_tokenize(line)
		pos_tokens = nltk.pos_tag(tokens)
		# print(pos_tokens)
		i = 0

		# Dicatate rhyme scheme
		if counter% 5 == 0:
			rhyme = words[len(words)-1].translate(translator)
			rep_token = nltk.word_tokenize(rhyme)
			pos_token = nltk.pos_tag(rep_token)
			print (pos_token)
		new_line = []
		print(pos_tokens)

		# Replacement algorithm
		for pos in pos_tokens:
			word = pos[0]

			# Maintain punctuation
			if word == "," or word == ".":
				new_line.append(word)
			else:
				replacement = ""

				offset = 1
				if (pos_tokens[len(pos_tokens) - 1][0] == "," or 
					pos_tokens[len(pos_tokens) - 1][1] == "." ):
					offset = 2

				if i == len(pos_tokens) - offset and (counter % 4 == 0 or 
					counter % 4 == 1 or counter % 4 == 3):
					rhymes = pronouncing.rhymes(rhyme)
					phones = pronouncing.phones_for_word(pos_tokens[len(pos_tokens) - offset][0])
					pat = pronouncing.stresses(random.choice(phones))
					choices = intersection(get_choices(word_pool, "^"+pat+"$"), rhymes)
					if (len(choices) > 3):
						replacement = random.choice(choices)
					else:
						replacement = random.choice(rhymes)
					rep_token = nltk.word_tokenize(replacement)
					pos_token = nltk.pos_tag(rep_token)
					try_counter = 0
					print(choices)
					while (pos_token[0][1] != pos[1] or not replacement in word_pool) and len(choices) > 0 and try_counter < 10:
						
						replacement = random.choice(choices)
						rep_token = nltk.word_tokenize(replacement)
						choices.remove(replacement)

					print("Adding 1" + replacement)
					new_line.append(replacement)
				else:
					choices = pronouncing.phones_for_word(word)
					try_counter = 0
					if len(choices) > 0:

						pat = pronouncing.stresses(random.choice(choices))
						choices = get_choices(word_pool, "^"+pat+"$")
						replacement = random.choice(choices)
						rep_token = nltk.word_tokenize(replacement)
						pos_token = nltk.pos_tag(rep_token)
						while (pos_token[0][1] != pos[1] or not 
							replacement in word_pool) and try_counter < 100:
							replacement = random.choice(choices)
							rep_token = nltk.word_tokenize(replacement)
							pos_token = nltk.pos_tag(rep_token)
							try_counter += 1
					if (try_counter == 100):
						# print("TRY_COUNTER")
						new_line.append(word)
					else:
						# print("Adding 2 " + replacement)
						new_line.append(replacement)

			i+=1

		add = ' '.join(new_line)	
		out.append(add)
		counter += 1
	
	# print('\n'.join(out))
	joined = '\n'.join(out)
	output.write(joined)


"""
Given a word pool and a pattern, create a list of words that are common and have
a 
"""
def get_choices(word_pool, pat):
	choices = pronouncing.search_stresses(pat)
	new_list = []
	for word in word_pool:
		if word in choices:
			new_list.append(word)

	return new_list

"""
Get the intersection between two lists. I took this from online!
"""
def intersection(lst1, lst2): 
    lst3 = [value for value in lst1 if value in lst2] 
    return lst3


"""
Evaluate for repition and for rhymes
"""
def eval(poem):
	words = {}
	repition = 0
	for word in poem.split():
		if word not in words:
			words[word] = 1
		else:
			word[words] = word[words] + 1
	for word in words:
		repition += word[words] - 1
	i = 0
	prev_line = ""
	num_rhymes = 0
	rhyme_words = set()
	for line in poem.split("\n"):
		rhyme_words.add(line.split()[len(line.split()) - 1])

	for line in poem.split("\n"):	
		rhymes = pronouncing.rhymes(line.split()[len(line.split()) - 1])
		if (intersection(rhymes, rhyme_words) > 0):
			num_rhymes += 1
		
	return repition + num_rhymes

main()