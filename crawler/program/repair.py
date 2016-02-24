import utility as ut

originSnList = ["facebook", "twitter", "linkedin", "pinterest", "plus.google", "tumblr", "instagram", "VK", "flickr", "Vine", "youtube", "github"]
snList = ["youtube", "facebook", "twitter", "linkedin", "flickr", "instagram", "tumblr", "github", "pinterest", "plus.google"]
# def repairSNFile(path, fileName):
# 	sns = ut.readCommaLine2List(path, fileName)
# 	sns = chechDuplicate(sns)
# 	checkSNSequence(sns)

# Deprecated
# Description: Revise the id_record file error
def reviseRecord():
	with open("../data/google/id_record_file", 'r') as fi:
		with open("../data/google/id_record_repair_file", "w") as fo:
			fo.write(fi.readline())
			for i in range(0, 136):
				fo.write(fi.readline())
			string = fi.readline()
			start = 0
			while(start < len(string)):
				end = start+25
				line = string[start:end]
				fo.write(line+'\n')
				start = end

# Description: Revise the sequence of social network file
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

if __name__ == "__main__":
	reviseSocialNetwork()
