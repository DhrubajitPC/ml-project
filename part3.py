import copy

#variables to hold parsed data
word_set = []
tag_set = []
word_tag_pairs = []
sequences = []
sequence = []
count_word_tag = {}


def process_data(line,word_set,tag_set,word_tag_pairs, sequences):
	global sequence 
	if len(line)>1:
		sequence.append(line.strip())
		word_tag_pairs.append(line.split())
		word = line.split()[0].lower()
		tag = line.split()[1]
		if word not in word_set:
			word_set.append(word)
		if tag not in tag_set:
			tag_set.append(tag)
	else:
		sequences.append(sequence)
		sequence = []

# for line in open("test.txt","r"):
for line in open("npc/train","r"):
# for line in open("pos/train", "r"):
	process_data(line,word_set,tag_set,word_tag_pairs,sequences)

# print sequence
# sequence = [x for x in sequence if x!= []]
# sequences.append(sequence)

# sequences = [x for x in sequences if x != []]

#initializing two variables to hold transmission probabilities count of tag1 to tag2
transmission_probablities = {}
for i in tag_set:
	transmission_probablities["Startto%(i)s" %locals()] = 0.0
	transmission_probablities["%(i)stoEnd" %locals()] = 0.0
	for j in tag_set:
		transmission_probablities["%(i)sto%(j)s" % locals()] = 0.0

count_tag1_tag2 = copy.deepcopy(transmission_probablities)

#initialize dictionary to hold emission count
def get_count_word_tag(count_word_tag):
	for pair in word_tag_pairs:
		word = pair[0]
		tag = pair[1]
		string = "%(word)s_%(tag)s" %locals()
		if string not in count_word_tag:
			count_word_tag[string] = 0

	for pair in word_tag_pairs:
		word = pair[0]
		tag = pair[1]
		string = "%(word)s_%(tag)s" %locals()
		count_word_tag[string] +=1
	return count_word_tag


def get_tag_count(sequences,tag_set):
	tag_count = {"Start":1, "End": 1}

	for i in tag_set:
		count = 0
		for sequence in sequences:
			for element in sequence:
				tag = element.split()[-1]
				if tag == i:
					count+=1
		tag_count["%(i)s" %locals()] = count
	return tag_count

# print tag_count

def get_count_tag1_tag2(tag_set, sequences,count_tag1_tag2):
	for i in tag_set:
		for sequence in sequences:
			for element in range(len(sequence)):
				tag = sequence[element].split()[-1]
				if tag == i and element<len(sequence)-1:
					next_tag = sequence[element+1].split()[-1]
					count_tag1_tag2["%(tag)sto%(next_tag)s" %locals()]+=1


	for sequence in sequences:
		start_tag = sequence[0].split()[1]
		end_tag = sequence[-1].split()[1]
		count_tag1_tag2["Startto%(start_tag)s" %locals()] += 1
		count_tag1_tag2["%(end_tag)stoEnd" %locals()] += 1
	return count_tag1_tag2


# print count_tag1_tag2

def get_emission_probabilities(count_word_tag,tag_count):
	emission_probabilities = {}

	for i in count_word_tag:
		tag = i.rsplit("_",1)[1]
		emission_probabilities[i] = float(count_word_tag[i])/tag_count[tag]
	return emission_probabilities

def get_emission_probability(emission_probabilities, tag_count, word, tag):
	key = word + "_" + tag
	if 	key in emission_probabilities:
		return emission_probabilities[key]
	else:
		tag_count[tag]+=1
		return 1.0/tag_count[tag]


def pos_tagger(word_sequence):
	global emission_probabilities
	global tag_count
	global tag_set

	predicted_word_tag = []
	for word in word_sequence:
		# print word
		chosen_tag = ""
		max_emission_value = 0
		for tag in tag_set:
			emission_value = get_emission_probability(emission_probabilities,tag_count,word,tag)
			if emission_value>max_emission_value:
				max_emission_value = emission_value
				chosen_tag = tag
		predicted_word_tag.append([word,chosen_tag])
	return predicted_word_tag

def accuracy(word_tag, predicted_word_tag):
	count = 0
	for element in range(len(predicted_word_tag)):
		if predicted_word_tag[element][1] == word_tag[element][1]:
			count += 1
	return float(count)/len(predicted_word_tag)

def get_transmission_probabilities(transmission_probablities,count_tag1_tag2,tag_count,sequences):
	for i in transmission_probablities:
		x = i.split("to")
		tag = x[0]
		next_tag = x[1]
		if tag == "Start" or next_tag == "End":
			transmission_probablities[i] = float(count_tag1_tag2[i])/len(sequences)
		else:
			transmission_probablities[i] = float(count_tag1_tag2[i])/tag_count[tag]
	return transmission_probablities

def get_transmission_probability(transmission_probabilities,tag1,tag2):
	key = tag1 + "to" + tag2
	return transmission_probablities[key]




count_word_tag = get_count_word_tag(count_word_tag)

tag_count = get_tag_count(sequences,tag_set)

count_tag1_tag2 = get_count_tag1_tag2(tag_set,sequences,count_tag1_tag2)

transmission_probablities = get_transmission_probabilities(transmission_probablities,count_tag1_tag2,tag_count,sequences)

emission_probabilities = get_emission_probabilities(count_word_tag,tag_count)
# print count_word_tag
# print "transmission probabilities: ", transmission_probablities
# print "emmision probabilities: ", emission_probabilities
# print tag_count

##testing part
# test_data = open("pos/dev.in","r")
test_data = open("npc/dev.in", "r")
word_sequence = test_data.read().strip().split()
predicted_word_tag = pos_tagger(word_sequence)
# print predicted_word_tag

# test_output = open("pos/dev.out","r")
test_output = open("npc/dev.out","r")
word_tag=[]

for i in test_output.read().split("\n"):
	if i != "":
		word = i.split()[0]
		tag = i.split()[1]
		word_tag.append([word,tag])
# print word_tag

print accuracy(word_tag,predicted_word_tag)
