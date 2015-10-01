import utility as ut

# def repairSNFile(path, fileName):
# 	sns = ut.readCommaLine2List(path, fileName)
# 	sns = chechDuplicate(sns)
# 	checkSNSequence(sns)


def checkDuplicate(lists, primary):
	keys = list()
	dup_nums = list()
	for i in range(len(lists)):
		key = lists[i][primary]
		if key in keys:
			print("duplicate:"+key)
			dups.append(i)
		else:
			keys.append(key)
	for i in range(len(dups)-1,-1,-1):
		key = dups[i]
		lists.remove(key)
	return lists

if __name__ == "__main__":
	print("check")