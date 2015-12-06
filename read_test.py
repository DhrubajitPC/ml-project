import numpy as np

def insert_val(x, li):
	inserted = False
	for i in range(len(li)):
		if x> li[i]:
			j = len(li)-1
			while j>i:
				li[j] = li[j-1]
				j-=1
			li[i] = x
			inserted = True
			break
	return inserted,i
# li =[]
# for i in range(1,10):
# 	li.append(np.random.randint(10))
# print li

li2 = [4, 2, 8, 5, 8, 6, 7, 0, 0]

li2.sort(reverse = True)
# print li2

# x,y =  insert_val(0,li2)
# print x, y, li2


a = {1: 23, 2: 45}
if 1 in a:
	print "x"
else:
	print "y"