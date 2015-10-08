import utility as ut
import os

snList = ["youtube", "facebook", "twitter", "linkedin", "flickr", "instagram", "tumblr", "github", "pinterest", "plus.google"]

def createSNMapping():
	path = "../data/google/"
	fileName = "sn_file"
	snLists = ut.readCommaLine2List(path, fileName)
	fbMapping = list()
	twitterMapping = list()
	youtubeMapping = list()
	for snList in snLists:
		uid = snList[0]
		if snList[1] != "":
			youtubeMapping.append([snList[0],snList[1]])
		if snList[2] != "":
			fbMapping.append([snList[0],snList[2]])
		if snList[3] != "":
			twitterMapping.append([snList[0],snList[3]])
	ut.writeList2CommaLine("../data", "youtubeMapping", youtubeMapping)
	ut.writeList2CommaLine("../data", "fbMapping", fbMapping)
	ut.writeList2CommaLine("../data", "twitterMapping", twitterMapping)


def calEdges(sn):
	path = "../data/"
	fileName = "relationship_file"
	count = 0
	with open(path+sn+"/"+fileName, 'r') as fi:
		for line in fi:
			try:
				count = count + len(line.split(" ")[1].split(","))
			except:
				continue
	print(count)

def calNodes(sn):
	path = "../data/"
	fileName = "allid_file"
	ids = list()
	with open(path+sn+"/"+fileName, "r") as fi:
		for line in fi:
			uid = line.strip()
			if uid not in ids:
				ids.append(uid)
	print(len(ids))


if __name__ == "__main__":
	print("summary")
	# createSNMapping()
	# calEdges("twitter")
	calNodes("twitter")