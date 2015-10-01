import utility as ut

originSnList = ["facebook", "twitter", "linkedin", "pinterest", "plus.google", "tumblr", "instagram", "VK", "flickr", "Vine", "youtube", "github"]
snList = ["youtube", "facebook", "twitter", "linkedin", "flickr", "instagram", "tumblr", "github", "pinterest", "plus.google"]
# def repairSNFile(path, fileName):
# 	sns = ut.readCommaLine2List(path, fileName)
# 	sns = chechDuplicate(sns)
# 	checkSNSequence(sns)


def reviseRecord():
	with open("../data/google/id_record_file", 'r') as fi:
		with open("../data/google/id_record_repair_file", "w") as fo:
			for i in range(0, 136):
				fo.write(fi.readline())
			string = fi.readline()
			start = 0
			while(start < len(string)):
				end = start+25
				line = string[start:end]
				fo.write(line+'\n')
				start = end

def reviseSocialNetwork():
	with open("../data/google/sn_file", "r") as fi:
		with open("../data/google/sn_repair_file", "w") as fo:
			for line in fi:
				result = [""]*len(snList)
				parts = line.split(",")
				uid = parts[0]
				sns = parts[1:]
				for sn in sns:
					if sn.strip() != "":
						for j in range(len(snList)):
							if snList[j] in sn:
								result[j] = sn.strip()
								break
				fo.write(uid+","+",".join(result)+'\n')

def reviseProfile():
	count = 0
	tmp = list()
	with open("../data/google/profile_file", "r") as fi:
		lines = fi.readlines()
		for i in range(len(lines)):
			line = lines[i]
			# try:	
			# 	# check several line
			# 	int(line.split(",")[0])
			# 	if len(line.split(",")[0])!=21:
			# 		print(i+1)
			# except:
			# 	print(i+1)
			if line.count(",")!=40:
				tmp.append(str(i+1))
				count+=1

		print(count)
	with open("../data/google/profile_revised_row", "w") as fo:
		fo.write(",".join(tmp))
		# with open("../data/google/profile_repair_file", "w") as fo:
			# for line in fi:
				# 40 commas
				# line.count()

				# repair time title error

def checkDuplicate(lists, primary):
	keys = list()
	dup_nums = list()
	for i in range(len(lists)):
		key = lists[i][primary]
		if key in keys:
			print("duplicate:"+key)
			dup_nums.append(i)
		else:
			keys.append(key)
	print(len(dup_nums))
	# for i in range(len(dups)-1,-1,-1):
	# 	key = dups[i]
	# 	lists.remove(key)
	# return lists

if __name__ == "__main__":
	# print("check")

	# reviseRecord()
	# lists = ut.readCommaLine2List("../data/google/", "profile_file")
	# checkDuplicate(lists, 0)
	# reviseSocialNetwork()

	reviseProfile()