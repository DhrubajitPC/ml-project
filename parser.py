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

print word_set
print tag_set
print word_tag_pairs
print sequences