import numpy as np

f = open("/Users/ping/Dropbox/SUTDY3/MACHINE LEARNING/proj/NPC/testtest.rtf","r") #opens file with name of "test.txt"
myList = []
for line in f.readlines():

 myList.append(line.rstrip('\\\n'))
 
list = myList[6:]

orglist = []
for string in list:
    if string != '':
        a = string.split()
        orglist.append(a)
    
orglist[0] = orglist[0][2:]
    
# states are {0, I-NP, B-NP},{x,y,z} emission = count(1 -> state)/count(1)

def Epara(states,orglist):
    
    S = []
    for i in states:
        S.append(0)
        
    #initiailize 1st emit
    emit = []
    emitset = []
    
    emit.append([orglist[0][0],S])
    emitset.append(orglist[0][0])
    
    for input in orglist:
        
        for i in range(len(emit)):
            if input[0] not in emitset:
                emit.append([input[0],S])
                emitset.append(input[0])
            else: 
               for j in range(len(states)):
                   if input[1] == states[j]:
                       emit[i][1][j] += 1
    
    
            
    
    return emit
    
    