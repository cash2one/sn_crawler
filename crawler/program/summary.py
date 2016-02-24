import utility as ut
import networkx as nx
import os
import json

'''
Statistic
'''
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

# Description: Check if google profile, wall and twitter profile, wall exist
# def calCompleteData():
	

# Description: write userids whose post file error
def writeMissingGooglePosts():
	ids = ut.readLine2List("../data/google/", "ids_mapping")
	ids_parsed = list()
	ids_errors = list()
	for root, folder, filenames in os.walk("../data/google/wall"):
		ids_parsed = filenames
		ids_errors = list(set(ids)-set(ids_parsed))
		for filename in filenames:
			with open(os.path.join(root, filename), "r", errors="ignore") as fi:
				try:
					result = json.loads(fi.read())
					if type(result) == dict:
						ids_errors.append(filename)
				except:
					pass
	ut.writeList2Line("../data/stat/", "google_ids_post_errors", ids_errors)


if __name__ == "__main__":
	writeMissingGooglePosts()
	# google 
	# print("summary in google")
	# calEdges("google")
	# calNodes("google")

	# twitter
	# print("summary in twitter")
	# calEdges("twitter")
	# calNodes("twitter")