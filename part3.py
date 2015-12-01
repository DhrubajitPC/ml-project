import copy

word_set = []
tag_set = []
word_tag_pairs = []
sequences = []
sequence = []
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

for line in open("test.txt","r"):
# for line in open("npc/train","r"):
	process_data(line,word_set,tag_set,word_tag_pairs,sequences)

sequences.append(sequence)

transmission_probablities = {}
for i in tag_set:
	transmission_probablities["Startto%(i)s" %locals()] = 0.0
	transmission_probablities["%(i)stoEnd" %locals()] = 0.0
	for j in tag_set:
		transmission_probablities["%(i)sto%(j)s" % locals()] = 0.0

count_tag1_tag2 = copy.deepcopy(transmission_probablities)


tag_count_dict = {"Start":1, "End": 1}

for i in tag_set:
	count = 0
	for sequence in sequences:
		for element in sequence:
			tag = element.split()[-1]
			if tag == i:
				count+=1
	tag_count_dict["%(i)s" %locals()] = count

# print tag_count_dict

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




a = 0
for i in transmission_probablities:
	x = i.split("to")
	tag = x[0]
	next_tag = x[1]
	if tag == "Start" or next_tag == "End":
		transmission_probablities[i] = count_tag1_tag2[i]/len(sequences)
	else:
		transmission_probablities[i] = count_tag1_tag2[i]/tag_count_dict[tag]

print transmission_probablities