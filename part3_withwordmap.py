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
# for line in open("npc/train","r"):
for line in open("pos/train", "r"):
	process_data(line,word_set,tag_set,word_tag_pairs,sequences)


#initializing two variables to hold transmission probabilities count of tag1 to tag2
transmission_probabilities = {}
for i in tag_set:
	transmission_probabilities["Startto%(i)s" %locals()] = 0.0
	transmission_probabilities["%(i)stoEnd" %locals()] = 0.0
	for j in tag_set:
		transmission_probabilities["%(i)sto%(j)s" % locals()] = 0.0

count_tag1_tag2 = copy.deepcopy(transmission_probabilities)

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

def get_emission_probabilities(count_word_tag,tag_count):
	emission_probabilities = {}

	for i in count_word_tag:
		tag = i.rsplit("_",1)[1]
		emission_probabilities[i] = float(count_word_tag[i])/tag_count[tag]
	return emission_probabilities

new_word_set_mapper = {}
#Handle new words by adding them to emission table and guessing what they are.
#Special cases includes USR (@), URL (http://), HT (#)
#lazy handling maps word to existing word in word_set
#Break word into 2. e.g, word='word' --> (ord), (w, rd), (wo, d), (wor)
#if a word in word_set contains both, add them to a set. Priority is based on length.
def new_word(word):
	if (word not in new_word_set_mapper.keys()):
		word_permutation1 = []
		word_permutation2 = []
		for i in range(len(word)):
			word_permutation1.append(word[0:i])
			word_permutation2.append(word[i+1:len(word)])
		best_match = word_set[0] #default
		best_score = -9999
		for w in word_set:
			score = -(len(w)-len(word))**2 #negative number
			for wp1 in word_permutation1:
				if (wp1!='' and (wp1 in w)):
					score+=len(wp1)
			for wp2 in word_permutation2:
				if (wp2!='' and (wp2 in w)):
					score+=len(wp2)
			if (score > best_score):
				best_match = w
				best_score = score
				#print 'score: ', score, word, w
		#print 'new map! ', word, '-->', best_match
		new_word_set_mapper[word] = best_match
	return new_word_set_mapper[word]	
	
def get_emission_probability(emission_probabilities, tag_count, word, tag):
	key = word + "_" + tag
	if 	key in emission_probabilities:
		return emission_probabilities[key]
	else:
		if (not word in word_set): #new word
			if (word[0]=='@'):
				return 1.0 if (tag=='USR') else 0.0
			elif (word[:7]=='http://' or word[:8]=='https://'):
				return 1.0 if (tag=='URL') else 0.0
			elif (word[0]=='#'):
				return 1.0 if (tag=='HT') else 0.0
			#redirect to closest matched word
			return get_emission_probability(emission_probabilities, tag_count, new_word(word), tag)
		tag_count[tag]+=1
		return 1.0/(tag_count[tag])


def pos_tagger(word_list):
	global emission_probabilities
	global tag_count
	global tag_set

	predicted_word_tag = []
	for word in word_list:
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

def get_transmission_probabilities(transmission_probabilities,count_tag1_tag2,tag_count,sequences):
	for i in transmission_probabilities:
		x = i.split("to")
		tag = x[0]
		next_tag = x[1]
		if tag == "Start" or next_tag == "End":
			transmission_probabilities[i] = float(count_tag1_tag2[i])/len(sequences)
		else:
			transmission_probabilities[i] = float(count_tag1_tag2[i])/tag_count[tag]
	return transmission_probabilities

def get_transmission_probability(transmission_probabilities,tag1,tag2):
	key = tag1 + "to" + tag2
	return transmission_probabilities[key]


def viterbi(word_sequence, transmission_probabilities, emission_probabilities,tag_set, tag_count):
	memo = {}
	for k in range(1,len(word_sequence)+1):
		if k == 1:
			tag_memo = {}
			for tag in tag_set:
				transmission_probability = get_transmission_probability(transmission_probabilities,"Start", tag)
				emission_probability = get_emission_probability(emission_probabilities,tag_count,word_sequence[k-1],tag)
				tag_memo[tag] = (transmission_probability*emission_probability, tag)
			memo[k] = tag_memo
		else:
			tag_memo = {}
			for tag in tag_set:
				tag_memo[tag] = pi(k,tag,memo, word_sequence,tag_count,transmission_probabilities,emission_probabilities)
			memo[k] = tag_memo
	tag_memo={"End": ()}
	tag_memo["End"] = pi(len(word_sequence), "End", memo, word_sequence,tag_count,transmission_probabilities,emission_probabilities)
	memo[len(word_sequence)+1] = tag_memo
	return memo

def pi(k,v,memo,word_sequence, tag_count, transmission_probabilities,emission_probabilities):
	max_prob = 0.
	chosen_tag = ""
	for tag in memo[k-1]:
		if v=="End":
			transmission_probability = get_transmission_probability(transmission_probabilities,tag,"End")
			prob = memo[k-1][tag][0] * transmission_probability
		else:
			transmission_probability = get_transmission_probability(transmission_probabilities,tag,v)
			emission_probability = get_emission_probability(emission_probabilities,tag_count,word_sequence[k-1],tag)
			prob = transmission_probability*emission_probability*memo[k-1][tag][0]
		if prob>=max_prob:
			max_prob = prob
			chosen_tag = tag
	return (max_prob, chosen_tag)


count_word_tag = get_count_word_tag(count_word_tag)

tag_count = get_tag_count(sequences,tag_set)

count_tag1_tag2 = get_count_tag1_tag2(tag_set,sequences,count_tag1_tag2)

transmission_probabilities = get_transmission_probabilities(transmission_probabilities,count_tag1_tag2,tag_count,sequences)

emission_probabilities = get_emission_probabilities(count_word_tag,tag_count)

##testing part
test_data = "pos/dev.in"
# test_data = "npc/dev.in"
with open(test_data,"r") as f:
	raw_data = f.read()

data = raw_data.split("\n")

test_word_sequences = []
sequence = []
for i in data:
	if i == "":
		test_word_sequences.append(sequence)
		sequence = []
	else:
		sequence.append(i)

for i in reversed(test_word_sequences):
	if i != []:
		break
	else:
		test_word_sequences.remove(i)

sequence_length = []
for i in test_word_sequences:
	sequence_length.append(len(i))

word_list = raw_data.strip().split()
predicted_word_tag = pos_tagger(word_list)

tag_sequences =[]
for word_sequence in test_word_sequences:
	memo = viterbi(word_sequence, transmission_probabilities, emission_probabilities,tag_set, tag_count)
	tag_sequence=[]
	j = len(memo)
	tag = memo[j]["End"][1]
	j-=1
	while j>0:
		tag = memo[j][tag][1]
		tag_sequence.append(tag)
		j-=1
	tag_sequence.reverse()
	tag_sequences.append(tag_sequence)

#writing to file
def write_to_file_p2(p2_file, predicted_word_tag, sequence_length):
	string = ""
	count = sequence_length[0]
	x=0
	for i in predicted_word_tag:
		line = ""
		for j in i:
			line+= j + " "
		line+="\n"
		count-=1
		if count == 0:
			line+="\n"
			x+=1
			if x<(len(sequence_length)):
				count = sequence_length[x]
		string += line

	with open(p2_file,"w") as f:
		f.write(string)
# p2_file = "npc/dev.p2.out"
p2_file = "pos/dev.p2.out"
write_to_file_p2(p2_file,predicted_word_tag,sequence_length)

_file = "pos/dev.out"
# _file = "npc/dev.out"
with open(_file, "r") as f:
	test_output = f.read()

def get_actual_tag_sequences(test_output):
	tag=[]
	tags=[]
	for i in test_output.split("\n"):
		if i != "":
			word = i.split()[0]
			current_tag = i.split()[1]
			tag.append(current_tag)
		else:
			tags.append(tag)
			tag = []
	for i in reversed(tags):
		if i ==[]:
			tags.remove(i)
	return tags


def get_actual_word_tag_pairs(test_output):
	word_tag=[]

	for i in test_output.split("\n"):
		if i != "":
			word = i.split()[0]
			tag = i.split()[1]
			word_tag.append([word,tag])
	return word_tag

def viterbi_acc(l1,l2):
	count = 0
	total_count = 0
	for i in l1:
		total_count+=len(i)
	for i in range(len(l1)):
		for j in range(len(l1[i])):
			if l1[i][j] == l2[i][j]:
				count+=1
	return float(count)/total_count

#write part3
# p3_file = "npc/dev.p3.out"
p3_file = "pos/dev.p3.out"

def write_to_file_p3(p3_file, tag_sequences, raw_data):
	string = ""
	tag_list = sum(tag_sequences,[])
	count = len(raw_data.split())
	word_list = raw_data.split("\n")
	for i in range(count):
		if word_list[i]!="":
			string += word_list[i] + " " + tag_list[i] + "\n"
		else:
			string+= "\n"
	with open(p3_file, "w") as f:
		f.write(string)

actual_tag_sequences = get_actual_tag_sequences(test_output)
word_tag = get_actual_word_tag_pairs(test_output)

write_to_file_p3(p3_file,tag_sequences,raw_data)

print viterbi_acc(actual_tag_sequences,tag_sequences)
print accuracy(word_tag,predicted_word_tag)
