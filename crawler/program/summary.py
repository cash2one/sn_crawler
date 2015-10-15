import utility as ut
import networkx as nx
import os

snList = ["youtube", "facebook", "twitter", "linkedin", "flickr", "instagram", "tumblr", "github", "pinterest", "plus.google"]

# Input: google social network mapping
# Output: youtube mapping file, facebook mapping file, twitter mapping file
# Description: mapping files produced by google social network mapping
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


# Description: calculate the numbers of friend links in one social network
def calEdges(sn):
	print("edges in "+sn)
	path = "../data/"
	fileName = "relationship_file"
	g = nx.Graph()
	with open(path+sn+"/"+fileName, 'r') as fi:
		for line in fi:
			try:
				uids = line.split(" ")
				user = uids[0]
				friends = uids[1].split(",")
				for frined in friends:
					g.add_edge(user, frined)
			except:
				continue
	print(len(g.edges()))

# Description: calculate the numbers of users in one social network
def calNodes(sn):
	path = "../data/"
	fileName = "allid_file"
	g = nx.Graph()
	with open(path+sn+"/"+fileName, "r") as fi:
		for line in fi:
			uid = line.strip()
			g.add_node(uid)
	print(len(g.nodes()))


if __name__ == "__main__":

	createSNMapping()
	

	# google 
	# print("summary in google")
	# calEdges("google")
	# calNodes("google")

	# twitter
	# print("summary in twitter")
	# calEdges("twitter")
	# calNodes("twitter")