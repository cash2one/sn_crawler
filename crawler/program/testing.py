tmp = [1,2,3]
for id in tmp:
	print(id)
	tmp.remove(id)
	tmp.append(id+3)