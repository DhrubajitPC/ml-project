import copy

#variables to hold parsed data
word_set = []
tag_set = []
word_tag_pairs = []
sequences = []
sequence = []
count_word_tag = {}

#break data into program recognizable form for further processing
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

print 'processing data...'
		
#for line in open("test.txt","r"):
for line in open("pos/train", "r"):
	process_data(line,word_set,tag_set,word_tag_pairs,sequences)
	
print 'done processing data'

# #initializing two variables to hold transmission probabilities count of tag1 to tag2
# def populate_transmission_probabilities(transmission_probabilities):
	# for i in tag_set:
		# transmission_probabilities["startto%(i)s" %locals()] = 0.0
		# transmission_probabilities["%(i)stoend" %locals()] = 0.0
		# for j in tag_set:
			# transmission_probabilities["%(i)sto%(j)s" % locals()] = 0.0
			
#transmission_probabilities = {}
#count_tag_giventags = copy.deepcopy(transmission_probabilities)

def incr_dict_count(dict, key1, key2=None):
	key = key1 if key2==None else key1+ '_*_' + key2 #special splitter that should not be replicated by any of the tags
	if dict.has_key(key):
		dict[key] += 1
	else:
		dict[key] = 1
def get_dict_count(dict, key1, key2=None):
	key = key1 if key2==None else key1+ '_*_' + key2 #special splitter that should not be replicated by any of the tags
	if (dict.has_key(key)):
		return dict[key]
	return 0

#initialize and populate dictionary to hold emission count [word, tag]
def get_count_word_tag(count_word_tag):
	for pair in word_tag_pairs:
		incr_dict_count(count_word_tag, pair[0], pair[1])
			
	return count_word_tag

#populates tag_count
def get_tag_count(sequences):
	tag_count = {}

	for sequence in sequences:
		for element in sequence:
			tag = element.split()[1]
			incr_dict_count(tag_count, str(tag))
		incr_dict_count(tag_count, 'Start')
		incr_dict_count(tag_count, 'End')
	return tag_count

#sequences are broken at .
#count discriminative transmission probabilities based on n nearest tags, populating count_tag_giventags [tag, tag_sequence]
#special tags are -- for no tags (before or after start) ** for the tag's location, and ?? for any tag (independent) <- this last one is not used in current implementation
def get_count_tag_giventags(sequences, n=1):
	count_tag_giventags = {}
	giventags_count = {}
	for seq in sequences:
		seq2 = []
		helper = []
		for element in range(len(seq)):
			tag = seq[element].split()[1]
			helper.append(seq[element])
			if tag == '.' or element == len(seq)-1:
				seq2.append(helper)
				helper = []
		for sequence in seq2:
			for element in range(len(sequence)):
				for _n in range(1,n+1): #have all n values
					tag = sequence[element].split()[1]
					key = [sequence[i].split()[1] for i in range(max(0,element-_n),min(len(sequence),element+_n+1))] #limit to within sequence range
					key[_n if element-_n>0 else element] = '**'
					string_key = str(key)
					incr_dict_count(count_tag_giventags, tag, string_key)
					incr_dict_count(giventags_count, string_key)
					#left and right wildcards
					if (key[0]!='**'):
						string_key = str(['??' if k<1 else key[k] for k in range(len(key))])
						incr_dict_count(count_tag_giventags, tag, string_key)
						incr_dict_count(giventags_count, string_key)
					if (key[-1]!='**'):
						string_key = str(['??' if k>len(key)-2 else key[k] for k in range(len(key))])
						incr_dict_count(count_tag_giventags, tag, string_key)
						incr_dict_count(giventags_count, string_key)
	return count_tag_giventags, giventags_count

#compute emission probabilities based on word_count_tag and tag_count
def get_emission_probabilities(count_word_tag,tag_count):
	emission_probabilities = {}

	for word_tag in count_word_tag.keys():
		tag = word_tag.rsplit("_*_",1)[1] #splitting using special splitter
		emission_probabilities[word_tag] = float(count_word_tag[word_tag])/tag_count[tag]
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

#get emission probability from emission_probabilities given a word and a tag
def get_emission_probability(emission_probabilities, tag_count, word, tag):
	key = word + "_*_" + tag
	if 	key in emission_probabilities.keys():
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
			# elif (tag=='VBG'):
				# if (word[-3:]=='ing'):
					# return 1.0/(tag_count[tag]+1)
			# elif (tag=='VBD'):
				# if (word[-2:]=='ed'):
					# return 1.0/(tag_count[tag]+1)
				# elif (word[-1]=='d'):
					# return 0.5/(tag_count[tag]+1)
			# #TODO: find closest match
			# return 0.25/(tag_count[tag]+1) #1/(tag_count+1)
		#return 1.0/(tag_count[tag]+1) #1/(tag_count+1)
		return 1.0/(sum(tag_count.itervalues())+1) #1/(#ofWords+1)

# def pos_tagger(word_list):
	# global emission_probabilities
	# global tag_count
	# global tag_set

	# predicted_word_tag = []
	# for word in word_list:
		# chosen_tag = ""
		# max_emission_value = 0
		# for tag in tag_set:
			# emission_value = get_emission_probability(emission_probabilities,tag_count,word,tag)
			# if emission_value>max_emission_value:
				# max_emission_value = emission_value
				# chosen_tag = tag
		# predicted_word_tag.append([word,chosen_tag])
	# return predicted_word_tag

#compute transmission probabilities based on count_tag_giventags and giventags_count
def get_transmission_probabilities(count_tag_giventags,giventags_count):
	transmission_probabilities = {}
	for tp in count_tag_giventags.keys():
		x = tp.split("_*_")
		tag = x[0]
		next_tags = x[1]
		trans_prob = float(count_tag_giventags[tp])/giventags_count[next_tags]
		#unbiased probability
		transmission_probabilities[tp] = (trans_prob * giventags_count[next_tags])/(giventags_count[next_tags]+10)
	return transmission_probabilities

#get transmission probability given some tags
#refer to get_count_tag_giventags for the complicated details
def get_transmission_probability(transmission_probabilities,tag_index,tag_sequence,n,trim='n'):
	global tag_count 
	
	tag = tag_sequence[tag_index]
	key = [tag_sequence[i] for i in range(max(0,tag_index-n),min(len(tag_sequence),tag_index+n+1))] #limit to within sequence range
	key[n if tag_index-n>0 else tag_index] = '**'
	if (trim=='l'):
		key[0] = '??'
	elif (trim=='r'):
		key[-1] = '??'
	string_key = str(key)
	tp = get_dict_count(transmission_probabilities, tag, string_key)
	if (tp>0):
		return tp * (1.0 if trim=='n' else 1.0/(giventags_count[string_key]+1))
	else:
		if ((key[0]!='**' and key[-1]!='**') or n>1): #trimmable
			if (trim=='n'): #none
				if (key[0]!='**'):
					return get_transmission_probability(transmission_probabilities, tag_index, tag_sequence, n, trim='l')
				elif(key[-1]!='**'):
					return get_transmission_probability(transmission_probabilities, tag_index, tag_sequence, n, trim='r')
				elif(n>1):
					return get_transmission_probability(transmission_probabilities, tag_index, tag_sequence, n-1, trim='n')
			elif (trim=='l'): #left trim
				if(key[-1]!='**'):
					return get_transmission_probability(transmission_probabilities, tag_index, tag_sequence, n, trim='r')
				elif(n>1):
					return get_transmission_probability(transmission_probabilities, tag_index, tag_sequence, n-1, trim='n')
			else: #right trim
				if(n>1):
					return get_transmission_probability(transmission_probabilities, tag_index, tag_sequence, n-1, trim='n')
		return 1.0/(tag_count[tag]+1)

print 'counting tags...'		

count_word_tag = get_count_word_tag(count_word_tag)

tag_count = get_tag_count(sequences)

count_tag_giventags, giventags_count = get_count_tag_giventags(sequences, 1)

transmission_probabilities = get_transmission_probabilities(count_tag_giventags,giventags_count)

emission_probabilities = get_emission_probabilities(count_word_tag,tag_count)

print 'done counting tags.'

# for tp, val in transmission_probabilities.items():
        # print tp, '-->', val
# for em, val in emission_probabilities.items():
        # print em, '-->', val
	
#called by pos_tagger
#Obj function of this pos_tagger is trans(given other tags)*emm
def sequence_tagger(sequence,tags,transmission_probabilities, tagset, n=1):
	def objf(_tags=tags, log=False):
		ret = 0.0
		for element in range(len(_tags)):
			tp = get_transmission_probability(transmission_probabilities, element, _tags, n)
			ep = get_emission_probability(emission_probabilities, tag_count, sequence[element], _tags[element])
			ret+= (0.1*tp)*ep
			if (log):
				print _tags[element], tp, ep
		return ret
	initial_tags = copy.deepcopy(tags)
	best_objf = objf() # objf(log=True)
	changed = False #True #change this to true to enable transmission
	# print sequence
	# print tags
	# print 'initial objf:', best_objf
	
	while(changed):
		changed=False
		for i in range(len(tags)):
			best_tag = tags[i]
			for tag in tagset:
				tags[i] = tag
				_objf = objf(tags)
				if (_objf>best_objf):
					best_objf = _objf
					best_tag = tag
					changed=True
			tags[i] = best_tag
		#print 'Changed!:', objf()
	#print 'final objf:', objf(log=True)
	#print tags, initial_tags
	
	# brute force
	# max_for_level = len(tags)-1
	# for_level = max_for_level
	# counter = [0]*len(tags)
	# target = len(tagset)
	# while(counter[0]<target):
		# while(counter[for_level]<target):
			# tags[for_level] = tagset[counter[for_level]]
			# #print tags
			# new_objf = objf()
			# if (new_objf>best_objf):
				# best_objf = new_objf
				# print best_objf
				# best_tags = copy.deepcopy(tags)
			# counter[for_level]+=1
			# while(for_level<max_for_level):
				# for_level+=1
				# counter[for_level]=0
		# if (for_level>=0):
			# for_level = for_level-1
	return tags
	
			
#Custom made pos_tagger, employing brute force approach to assign tags.
#sequences refer to untagged sequence
def pos_tagger(sequences):
	global transmission_probabilities
	global emission_probabilities
	global tag_count
	
	sequences_pos_tags = []
	for seq in sequences:
		sequence_pos_tags = []
		#initialize tags with the best emission probabilities
		for element in range(len(seq)):
			best_initial_tag = [0.0, None]
			for tag in tag_count.keys():
				ep = get_emission_probability(emission_probabilities, tag_count, seq[element], tag)
				if (ep>best_initial_tag[0]):
					best_initial_tag = [ep, tag]
			sequence_pos_tags.append(best_initial_tag[1])
			
		new_pos_tags = []
		helper = 0
		for element in range(len(seq)): #break sequences on .
			tag = sequence_pos_tags[element]
			#helper.append(seq[element])
			if tag == '.' or element == len(seq)-1:
				seq2 = seq[helper:element+1]
				seq2tags = sequence_pos_tags[helper:element+1]
				helper = element+1
				#print len(seq), seq2tags
				tag_result = sequence_tagger(seq2, seq2tags, transmission_probabilities, tag_count.keys(), 1)
				for tr in tag_result:
					new_pos_tags.append(tr)
		sequences_pos_tags.append(new_pos_tags)
	return sequences_pos_tags

##testing part
#test_data = "pos/dev.in"
test_data = "pos/ml1.txt"

with open(test_data,"r") as f:
	raw_data = f.read()

data = raw_data.split("\n")

test_word_sequences = []
sequence = []
for i in data: #new sentence
	if i == "":
		test_word_sequences.append(sequence)
		sequence = []
	else:
		sequence.append(i)
#removing redundant sequences
for i in reversed(test_word_sequences):
	if i != []:
		break
	else:
		test_word_sequences.remove(i)

sequence_length = []
for i in test_word_sequences:
	sequence_length.append(len(i))

predicted_word_tag = pos_tagger(test_word_sequences)

#Read answer 'tags'
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

#write part5
#p5_file = "pos/dev.p5.out"
p5_file = "pos/ml1.out.txt"

def write_to_file(p3_file, tag_sequences_p3, raw_data):
	string = ""
	tag_list = sum(tag_sequences_p3,[])
	count = len(raw_data.split())
	word_list = raw_data.split("\n")
	for i in range(count):
		if word_list[i]!="":
			string += word_list[i] + " " + tag_list[i] + "\n"
		else:
			string+= "\n"
	with open(p3_file, "w") as f:
		f.write(string)
		
#compute the accuracy of the algorithm
def viterbi_acc(l1,l2):
	count = 0
	total_count = 0
	for i in l1:
		total_count+=len(i)
	for i in range(len(l1)):
		for j in range(len(l1[i])):
			#print l1[i][j], l2[i][j]
			if l1[i][j] == l2[i][j]:
				count+=1
	return float(count)/total_count

# _file = "pos/dev.out"
# with open(_file, "r") as f:
	# test_output = f.read()
	
##Comparing Accuracy
#actual_tag_sequences = get_actual_tag_sequences(test_output)

write_to_file(p5_file,predicted_word_tag,raw_data)

print new_word_set_mapper

#print 'Accuracy:', viterbi_acc(actual_tag_sequences,predicted_word_tag)
