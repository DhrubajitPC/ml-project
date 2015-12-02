import numpy as np
import operator 
##parsed training data of format: [['word','tag']...] returns emission of format: [['word', [e1,e2,e3]]...]
f = open("/Users/ping/Dropbox/SUTDY3/MACHINE LEARNING/proj/NPC/testtest.rtf","r") #opens file with name of "test.txt"
myList = []
for line in f.readlines():

 myList.append(line.rstrip('\\\n'))
 
list = myList[6:31]

orglist = []
for string in list:
    if string != '' and '}':
        a = string.split()
        orglist.append(a)
    
orglist[0] = orglist[0][2:]



f2 = open("/Users/ping/Dropbox/SUTDY3/MACHINE LEARNING/proj/NPC/test2.rtf","r") #opens file with name of "test.txt"
myList2 = []
for line in f2.readlines():

 myList2.append(line.rstrip('\\\n'))
 
list2 = myList2[6:25]

orglist2 = []
for string in list2:
    if string != '' and '}':
        a = string.split()
        orglist2.append(a)
    
orglist2[0] = orglist2[0][2:]
##


states = ['O','I-NP','B-NP']
emitpt1 = Epara(states, orglist)[2] #emission without average
emitset = Epara(states, orglist)[1] #list of words


def Epara(states,orglist):#returns emission parameters for training, the words w/o repeats, emission w/o avg
    
    S = [0,0,0]
    emit = []
    emitset = []
    
    for i in orglist:
        Stemp = S
        c = states.index(i[1]) #position of the new x state
        Stemp[c] = 1
        if i[0] not in emitset:
            emit.append([i[0], Stemp])
            emitset.append(i[0])
            S = [0,0,0] 
        else:
            a = emitset.index(i[0]) # the position of of the repeated x
            b = states.index(i[1]) #position of state in output
            emit[a][1][b] += 1
    emit2 = emit
    for i in emit2:
        i[1] = [x/sum(i[1]) for x in i[1]]
        
    return emit2, emitset, emit
    
def Epara2(states, emitpt1, emitset, orglist2): #emission for new test values
    n = []
    for i in emitset:
        n.append(0.0)
        
    for i in orglist2:
        if i[0] not in emitset:
            emitset.append(i[0])
            emitpt1.append([i[0], [1.0,1.0,1.0]])
            n.append(0.0)
            
        else:
           a = emitset.index(i[0]) 
           n[a] += 1
           
    emitx = emitpt1
    for i in emitx:
        i[1] = [x/(sum(i[1])+n[emitx.index(i)]) for x in i[1]]
        
    return emitx, n
        
            
        

    
    