tags = ['O','O','O','O']
tagset = ['A','B','C']
max_for_level = len(tags)-1
for_level = max_for_level
counter = [0]*len(tags)
target = len(tagset)
while(counter[0]<target):
    while(counter[for_level]<target):
        tags[for_level] = tagset[counter[for_level]]
        print for_level, [tags[i] for i in range(len(tags))]
        counter[for_level]+=1
        while(for_level<max_for_level):
            for_level+=1
            counter[for_level]=0
    if (for_level>=0):
        for_level = for_level-1
