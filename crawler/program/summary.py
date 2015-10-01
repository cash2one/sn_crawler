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



if __name__ == "__main__":
	print("summary")
	createSNMapping()