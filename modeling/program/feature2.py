import os
import multiprocessing as mp
import threading as td
import json
import networkx as nx
import utility as ut
# from scipy.sparse import lil_matrix
import math
import time
import re
# name matching
import pyxdameraulevenshtein
import name_tools
# language detection
import langid
import langdetect
from textblob import TextBlob

rule = re.compile("[`~!@#$%^&*()-_=+{}|\"\' ]")
langs_not_western = ["zh", "ja", "ko"]
# langs = ["zh"]
outputPath = "../output/"
interPath = "../intermediate/"
inputPath = "../data/"

featureFileName = "features"
featureFileNamePrevious = "features-0203"
popularCountFileName = "mpCount"
gtLooseFileName = "gt_loose"
gtStrictFileName = "gt_strict"
twitterNameIdFileName = "twitterNameId"
twitterIdNameFileName = "twitterIdName"


'''
Main
'''
def getUsersFeatures(procNum = 16):
	# init user pair by mapping
	gts = ut.readCommaLine2List(interPath, gtStrictFileName)
	sn1 = "google"
	sn2 = "twitter"
	users_sn1 = list()
	users_sn2 = list()
	# scoresMatrix = lil_matrix((len(gts), len(gts)))
	scoresMatrix = dict()
	for gt in gts:
		users_sn1.append(gt[0])
		users_sn2.append(gt[1])
	# build graph
	print("build graph")
	s = time.time()
	g1, g2, g0 = buildGraphs(users_sn1, users_sn2)
	e = time.time()
	print("build graph over cost: "+str(e-s))
	# for profile using

	print("popular count")
	s = time.time()
	writeMostPopularCount(g1, sn1, users_sn1, g2, sn2, users_sn2)
	e = time.time()
	print("popular count over cost: "+str(e-s))

	print("calculate features start")
	# calculate features
	s = time.time()
	pairs = [(a,b) for a in range(len(gts)) for b in range(len(gts)) if b>=a]
	twitterIdName = ut.readJson2Dict(interPath, twitterIdNameFileName)
	twitterNameId = ut.readJson2Dict(interPath, twitterNameIdFileName)

	profileGoogle, profileTwitter, wallGoogle, wallTwitter, textGoogle, textTwitter = readData(users_sn1, users_sn2, twitterIdName)

	# 
	# for pair in pairs:
	# 	print(pair)
	# 	scores = getScores(sn1, users_sn1[pair[0]], sn2, users_sn2[pair[1]], g1, g2, g0)
	# 	scoresMatrix[(pair[0], pair[1])] = scores

	# parallel
	batchNum = round(len(pairs)/procNum)
	procs = list()
	q = mp.Queue()

	for i in range(procNum):
		if i == procNum-1:
			batchPairs = pairs[i*batchNum:]
		else:
			batchPairs = pairs[i*batchNum:(i+1)*batchNum]
		# p = td.Thread(target=getScoresWorker, args=(batchPairs, sn1, users_sn1, sn2, users_sn2, g1, g2, g0, q))
		# p = mp.Process(target=getScoresWorker, args=(batchPairs, sn1, users_sn1, sn2, users_sn2, g1, g2, g0, q, profileGoogle, profileTwitter, wallGoogle, wallTwitter, textGoogle, textTwitter))
		p = td.Thread(target=getScoresWorker, args=(batchPairs, sn1, users_sn1, sn2, users_sn2, g1, g2, g0, q, profileGoogle, profileTwitter, wallGoogle, wallTwitter, textGoogle, textTwitter))
		p.start()
		procs.append(p)
	print("update start")
	for i in range(len(pairs)):
		print(i)
		result = q.get()
		# scoresMatrix.update(result)
		scoresMatrix[result["key"]] = result["value"]
	print("update over")
	print(len(scoresMatrix))
	for proc in procs:
		proc.join()

	# output feature
	with open(outputPath+featureFileName, "w") as fo:
		for i in range(len(gts)):
			for j in range(len(gts)):
				if i == j:
					rank = 1
				else:
					rank = 0
				if i > j:
					scores = scoresMatrix[(j, i)]
				else:
					scores = scoresMatrix[(i, j)]
				outputStr = getFeatureStr(rank, users_sn1[i], users_sn2[j], scores)
				fo.write(outputStr)

	# with open(outputPath+featureFileName, "w") as fo:
	# 	for i in range(len(gts)):
	# 		print(users_sn1[i])
	# 		print(i)
	# 		for j in range(len(gts)):
	# 			print(j)
	# 			if i == j:
	# 				rank = 1
	# 			else:
	# 				rank = 0
	# 			scores = getScores(sn1, users_sn1[i], sn2, users_sn2[j], g1, g2, g0)
	# 			outputStr = getFeatureStr(rank, users_sn1[i], users_sn2[j], scores)
	# 			fo.write(outputStr)
	e = time.time()
	print("write feature costs:" + str(e-s))

# def getScoresWorker(pairs, sn1, users_sn1, sn2, users_sn2, g1, g2, g0, q):
def getScoresWorker(pairs, sn1, users_sn1, sn2, users_sn2, g1, g2, g0, q, profileGoogle, profileTwitter, wallGoogle, wallTwitter, textGoogle, textTwitter):
	for pair in pairs:
		print(pair)
		score = calScores(users_sn1[pair[0]], users_sn2[pair[1]], g1, g2, g0, profileGoogle, profileTwitter, wallGoogle, wallTwitter, textGoogle, textTwitter, sn1, sn2)
		q.put({"key": pair, "value": score})

def calScores(userGoogle, userTwitter, g1, g2, g0, profileGoogle, profileTwitter, wallGoogle, wallTwitter, textGoogle, textTwitter, sn1, sn2):
	profile1 = profileGoogle[userGoogle]
	profile2 = profileTwitter[userTwitter]
	posts1 = wallGoogle[userGoogle]
	posts2 = wallTwitter[userTwitter]
	text1 = textGoogle[userGoogle]
	text2 = textTwitter[userTwitter]
	scores = calProfileScore(sn1, profile1, sn2, profile2) + calSocialScore(g1, sn1, userGoogle, g2, sn2, userTwitter, g0)+ calBehaviorScore(posts1, posts2, text1, text2)
	return scores


def readData(users_google, users_twitter, twitterIdName):
	profileGoogle = dict()
	profileTwitter = dict()
	wallGoogle = dict()
	wallTwitter = dict()
	textGoogle = dict()
	textTwitter = dict()
	for user in users_google:
		profileGoogle[user] = ut.readJson2Dict(interPath+"google/profile/", user)
		wallGoogle[user] = ut.readJson2Dict(interPath+"google/wall/", user)
		textGoogle[user] = ut.readJson2Dict(interPath+"google/text/", user)
	for user in users_twitter:
		twitterName = twitterIdName[user]
		profileTwitter[user] = ut.readJson2Dict(interPath+"twitter/profile/", twitterName)
		wallTwitter[user] = ut.readJson2Dict(interPath+"twitter/wall/", twitterName)
		textTwitter[user] = ut.readJson2Dict(interPath+"twitter/text/", twitterName)
	return profileGoogle, profileTwitter, wallGoogle, wallTwitter, textGoogle, textTwitter
	print("load file over")

def getScores(sn1, user1, sn2, user2, g1, g2, g0):
	# read the twitter name id mapping file
	twitterIdName = ut.readJson2Dict(interPath, twitterIdNameFileName)
	if sn2 == "twitter":
		user2_name = twitterIdName[user2]
		scores = getProfileScore(sn1, user1, sn2, user2_name)+getSocialScore(sn1, user1, sn2, user2, g1, g2, g0)+getBehaviorScore(sn1, user1, sn2, user2_name)
	elif sn1 == "twitter":
		user1_name = twitterIdName[user1]
		scores = getProfileScore(sn1, user1_name, sn2, user2)+getSocialScore(sn1, user1, sn2, user2, g1, g2, g0)+getBehaviorScore(sn1, user1_name, sn2, user2)
	else:
		scores = getProfileScore(sn1, user1, sn2, user2)+getSocialScore(sn1, user1, sn2, user2, g1, g2, g0)+getBehaviorScore(sn1, user1, sn2, user2)
	return scores


# Input: sn1 name, userid1, sn2 name, userid2
# Return: 4 features (one popular for social), list of score in each profile attribute
def getProfileScore(sn1, user1, sn2, user2):
	# open intermediate file and input
	profile1 = dict()
	profile2 = dict()
	with open(interPath+sn1+"/profile/"+user1, "r") as fi:
		profile1 = json.loads(fi.read())
	with open(interPath+sn2+"/profile/"+user2, "r") as fi:
		profile2 = json.loads(fi.read())
	scoresProfile = calProfileScore(sn1, profile1, sn2, profile2)
	return scoresProfile

# Input: sn1 name, userid1, sn2 name, userid2, network graph
# Return: 19 features (one popular in profile) , list of score in each social attribute
def getSocialScore(sn1, user1, sn2, user2, g1, g2, g0):
	# open intermediate file
	scoresSocial = calSocialScore(g1, sn1, user1, g2, sn2, user2, g0)
	return scoresSocial


# Input: sn1 name, userid1, sn2 name, userid2
# Return: 34 features, list of score in each behavior attribute
def getBehaviorScore(sn1, user1, sn2, user2):
	posts1 = ut.readJson2Dict(interPath+sn1+"/wall/", user1) 
	posts2 = ut.readJson2Dict(interPath+sn2+"/wall/", user2)
	text1 = ut.readJson2Dict(interPath+sn1+"/text/", user1)
	text2 = ut.readJson2Dict(interPath+sn2+"/text/", user2)
	scoresBehavior = calBehaviorScore(posts1, posts2, text1, text2)
	return scoresBehavior

# Description:
# Input:
# Output:
# Return: boolean if two users should be testing
# def filterPair(sn1, user1, sn2, user2):




'''
Graph
'''
# Description: This file is for getting the score by extracting the feature of profile matching, behavior modeling, and social feature

# node, "twitter": twitterId, "neighbor_twitter": {"gid", "tid"}
def buildGraphs(users1, users2):
	# google graph
	print("google graph")
	googleDiGraph = buildDiGraph(interPath+"google/relationship_file", users1)
	# twitter graph 
	print("twitter graph")
	twitterDiGraph = buildDiGraph(interPath+"twitter/relationship_file_revise", users2)
	# full graph
	print("full graph")
	allDiGraph = nx.DiGraph()
	allDiGraph.add_edges_from(googleDiGraph.edges())
	allDiGraph.add_edges_from(twitterDiGraph.edges())
	# add mapping info	
	gts = ut.readCommaLine2List(interPath, gtStrictFileName)
	for gt in gts:
		googleId = gt[0]
		twitterId = gt[1]
		googleDiGraph.add_node(googleId, {"twitter":twitterId})
		twitterDiGraph.add_node(twitterId, {"google":googleId})
		allDiGraph.add_edge(googleId, twitterId)
		allDiGraph.add_edge(twitterId, googleId)
	# build neighbor mapping list
	for gt in gts:
		googleId = gt[0]
		twitterId = gt[1]
		neighbors_g = googleDiGraph.neighbors(googleId)
		neighbors_t = twitterDiGraph.neighbors(twitterId)
		for n in neighbors_g:
			result = googleDiGraph.node[googleId].get("neighbor_twitter", dict())
			if googleDiGraph.node[n].get("twitter", 0)!=0:
				result[n] = googleDiGraph.node[n]["twitter"]
				googleDiGraph.node[googleId]["neighbor_twitter"] = result
		for n in neighbors_t:
			result = twitterDiGraph.node[twitterId].get("neighbor_google", dict())
			if twitterDiGraph.node[n].get("google", 0) !=0:
				result[n] = twitterDiGraph.node[n]["google"]
				twitterDiGraph.node[twitterId]["neighbor_google"] = result
	return googleDiGraph, twitterDiGraph, allDiGraph



def buildGraph(fileName, users):
	g = nx.Graph()
	with open(fileName, 'r') as fi:
		for index, line in enumerate(fi):
			ids = line.split(" ")
			user = ids[0]
			print(index)
			if user not in users:
				continue
			try:
				friends = ids[1].split(",")
				for friend in friends:
					g.add_edge(user, friend)
			except:
				g.add_node(user)
	return g


def buildDiGraph(fileName, users):
	dg = nx.DiGraph()
	with open(fileName, 'r') as fi:
		for index, line in enumerate(fi):
			ids = line.split(" ")
			user = ids[0]
			print(index)
			if user not in users:
				continue
			else:
				print(user)
			try:
				friends = ids[1].split(",")
				for friend in friends:
					dg.add_edge(user, friend)
			except:
				dg.add_node(user)
	return dg

'''
Candidata Generation
'''

def getCandidates():
	print("get candidates")

'''
Profile
'''

# need specific weight?
# name, displayName, place, popular in sn1, popular in sn2
def calProfileScore(sn1, profile1, sn2, profile2):
	scores = list()
	scores.append(calNameScore(profile1, profile2))
	scores.append(calDisplayNameScore(profile1, profile2))
	scores.append(calPlaceScore(profile1, profile2))
	scores.append(calPolularScore(sn1, profile1, sn2, profile2))
	scores.append(calTagScore(profile1, profile2))
	return scores
	# name
	# displayName
	# placesLived
	# description: not yet
	# circledByCount



def calNameScore(profile1, profile2):
	name1 = profile1["name"]
	name2 = profile2["name"]
	lang1 = profile1["nameLang"]
	lang2 = profile2["nameLang"]
	if lang1 == lang2:
		if lang1 in langs_not_western:
			return calNotWesternName(name1, name2)
		else:
			# return name_tools.match(name1, name2)
			return calNotWesternName(name1, name2)
	else:
		if len(name1)>3 and len(name2)>3:
			# 避免有時候翻譯錯，所以不用name_tools 例如chen shih ying 陳世穎卻翻成chen shiying
			try:
				if lang1 != "en":
					name1 = str(TextBlob(name1).translate(to="en"))
			except:
				pass
			try:
				if lang2 != "en":
					name2 = str(TextBlob(name2).translate(to="en"))
			except:
				pass
			return 1-pyxdameraulevenshtein.normalized_damerau_levenshtein_distance(name1, name2)
		else:
			return 1-pyxdameraulevenshtein.normalized_damerau_levenshtein_distance(name1, name2)


def calDisplayNameScore(profile1, profile2):
	name1 = profile1["displayName"]
	name2 = profile2["displayName"]
	lang1 = profile1["displayNameLang"]
	lang2 = profile2["displayNameLang"]
	if lang1 == lang2:
		return 1-pyxdameraulevenshtein.normalized_damerau_levenshtein_distance(name1, name2)
	else:
		if len(name1)>3 and len(name2)>3:
			try:
				if lang1 != "en":
					name1 = str(TextBlob(name1).translate(to="en"))
				if lang2 != "en":
					name2 = str(TextBlob(name2).translate(to="en"))
			except:
				pass
			return 1-pyxdameraulevenshtein.normalized_damerau_levenshtein_distance(name1, name2)
		else:
			return 1-pyxdameraulevenshtein.normalized_damerau_levenshtein_distance(name1, name2)


def calNotWesternName(name1, name2):
	if name1==name2:
		return 1
	else:
		normName1 = normStr(name1)
		normName2 = normStr(name2)
		if normName1 == normName2:
			return 0.9
		if normName1 in normName2 or normName2 in normName1:
			return 0.8
		else:			
			return 0


def normStr(string):
	# string = string.replace("@", "")
	string = re.sub(rule, "", string)
	return string

# def findLongestSubStrin():

def calPlaceScore(profile1, profile2):
	# calculate the distance future
	score = 0
	places1 = profile1["placesLived"]
	places2 = profile2["placesLived"]
	# compare primary place
	priPlace1 = str()
	allPlaces1 = list()
	priPlace2 = str()
	allPlaces2 = list()
	for place in places1:
		if place.get("primary", 0) != 0:
			priPlace1 = place["value"]
		allPlaces1.append(place["value"])
	for place in places2:
		if place.get("primary", 0) != 0:
			priPlace2 = place["value"]
		allPlaces2.append(place["value"])

	score = comparePlace(priPlace1, priPlace2, True)
	total = len(allPlaces1) * len(allPlaces2) -1
	if (total)>0:
		for p1 in allPlaces1:
			for p2 in allPlaces2:
				if p1 == priPlace1 and p2 == priPlace2:
					pass
				else:
					score += comparePlace(p1, p2, False)/total
	return score

	# compare with other place

def comparePlace(place1, place2, primary_bool):
	score = float()
	count = int()
	place1 = place1.lower()
	place2 = place2.lower()
	if place1 == "" or place2 == "":
		return 0
	if place1 == place2:
		return 1
	zones1 = place1.split(",")
	zones1.reverse()
	zones2 = place2.split(",")
	zones2.reverse()
	for i in range(len(zones1)):
		zone1 = zones1[i]
		for j in range(len(zones2)):
			zone2 = zones2[j]
			if zone1 == zone2:
				count = count+1
	if count == 0 and primary_bool:
		return -1
	if len(zones1) > len(zones2):
		score = count/len(zones1)
		return score
	else:
		score = count/len(zones2)
		return score




# def calDescriptionScore(profile1, profile2):

def calPolularScore(sn1, profile1, sn2, profile2):
	# highest count in each social network
	try:
		mpCount = readMostPopularCount()
		mpRatio1 = float(profile1["circledByCount"])/mpCount[sn1]
		mpRatio2 = float(profile2["circledByCount"])/mpCount[sn2]

		if mpRatio2>mpRatio1:
			ratio = mpRatio1/mpRatio2
		else:
			ratio = mpRatio2/mpRatio1
		return ratio
	except:
		return 1



def calTagScore(profile1, profile2):
	tags1 = profile1["tags"]
	tags2 = profile2["tags"]
	return len(set(tags1) and set(tags2))

'''
Social
'''
def calSocialScore(g1, sn1, u1, g2, sn2, u2, g0):
	scores = list()
	# common friends
	common_n = list()
	common_n_num = 0

	u1_neighbors = g1.neighbors(u1)
	u2_neighbors = g2.neighbors(u2)
	u1_neighbors_map_dict = g1.node[u1].get("neighbor_"+sn2, dict())
	u2_neighbors_map_dict = g2.node[u2].get("neighbor_"+sn1, dict())
	u1_neigh_num = len(u1_neighbors)
	u2_neigh_num = len(u2_neighbors)
	u1_neigh_num_map = len(u1_neighbors_map_dict)
	u2_neigh_num_map = len(u2_neighbors_map_dict)

	# [{google: gid, twitter: tid}]
	for n, n_map in u1_neighbors_map_dict.items():
		if n_map in u2_neighbors_map_dict:
			common_n.append({sn1: n, sn2: n_map})
	common_n_num = float(len(common_n))

	# jaccard's: for two social friend, all friends, all mapping friends
	overlap_n = 0
	overlap_n_g1 = 0
	overlap_n_g2 = 0
	overlap_n_map = 0
	overlap_n_map_g1 = 0
	overlap_n_map_g2 = 0

	if common_n_num == 0:
		overlap_n_g1 = 0
		overlap_n_g2 = 0
		overlap_n = 0
		overlap_n_map = 0
		overlap_n_map_g1 = 0
		overlap_n_map_g2 = 0
	else:
		overlap_n_g1 = common_n_num/u1_neigh_num
		overlap_n_g2 = common_n_num/u2_neigh_num
		overlap_n = common_n_num/(u1_neigh_num+u2_neigh_num-common_n_num)
		overlap_n_map = common_n_num/(u1_neigh_num_map+u2_neigh_num_map-common_n_num)
		overlap_n_map_g1 = common_n_num/(u1_neigh_num_map)
		overlap_n_map_g2 = common_n_num/(u2_neigh_num_map)
	overlap = [overlap_n, overlap_n_g1, overlap_n_g2, overlap_n_map, overlap_n_map_g1, overlap_n_map_g2]

	# adamic/adar measure: g1, g2, g1+g2, map, map_g1, map_g2
	aa_n = 0
	aa_n_g1 = 0
	aa_n_g2 = 0
	aa_n_map = 0
	aa_n_map_g1 = 0
	aa_n_map_g2 = 0
	for n in common_n:
		common_n_sn1 = n[sn1]
		common_n_sn2 = n[sn2]
		cn_sn1_neighbors_num = len(g1.neighbors(common_n_sn1))
		cn_sn2_neighbors_num = len(g2.neighbors(common_n_sn2))
		cn_sn1_neighbors_map_num = len(g1.node[common_n_sn1].get("neighbor_"+sn2, dict()))
		cn_sn2_neighbors_map_num = len(g2.node[common_n_sn2].get("neighbor_"+sn1, dict()))
		aa_n = calAdamic(aa_n, cn_sn1_neighbors_num+cn_sn2_neighbors_num)
		aa_n_g1 = calAdamic(aa_n_g1, cn_sn1_neighbors_num)
		aa_n_g2 = calAdamic(aa_n_g2, cn_sn2_neighbors_num)
		aa_n_map = calAdamic(aa_n_map, cn_sn1_neighbors_map_num+cn_sn2_neighbors_map_num)
		an_n_map_g1 = calAdamic(aa_n_map_g1, cn_sn1_neighbors_map_num)
		aa_n_map_g2 = calAdamic(aa_n_map_g2, cn_sn2_neighbors_map_num)
	aa = [aa_n, aa_n_g1, aa_n_g2, aa_n_map, aa_n_map_g1, aa_n_map_g2]
 
	# pa: all friends, all mapping friends
	pa = u1_neigh_num * u2_neigh_num
	pa_map = u1_neigh_num_map * u2_neigh_num_map

	# tcfc: all friends, all mapping friends
	tfcf = 0
	tfcf_map = 0
	for n in common_n:
		common_n_sn1 = n[sn1]
		common_n_sn2 = n[sn2]
		cf_neighbors_sn1 = g1.neighbors(common_n_sn1)
		cf_neighbors_sn2 = g2.neighbors(common_n_sn2)
		cf_neighbors_sn1_map_dict = g1.node[common_n_sn1].get("neighbor_"+sn2, dict())
		cf_neighbors_sn2_map_dict = g2.node[common_n_sn2].get("neighbor_"+sn1, dict())
		common_c1 = set(u1_neighbors).intersection(cf_neighbors_sn1)
		common_c2 = set(u2_neighbors).intersection(cf_neighbors_sn2)
		common_c1_map = set(u1_neighbors_map_dict.keys()).intersection(cf_neighbors_sn1_map_dict.keys())
		common_c2_map = set(u2_neighbors_map_dict.keys()).intersection(cf_neighbors_sn2_map_dict.keys())
		tfcf += len(common_c1) * len(common_c2)
		tfcf_map += len(common_c1_map) * len(common_c2_map)


	# shortest path reverse
	spath = float()
	has_e = bool()
	# remove the edge first
	if g0.has_edge(u1, u2):
		has_e = True
		g0.remove_edge(u1, u2)
		g0.remove_edge(u2, u1)
	try:
		spath = 1/float(nx.shortest_path_length(g0, source=u1, target=u2))
	except:
		spath = 0
	# add back the mapping
	if has_e:
		g0.add_edge(u1, u2)
		g0.add_edge(u2, u1)

	scoresSocial = [common_n_num] + overlap + aa + [pa, pa_map, tfcf, tfcf_map, spath]
	return scoresSocial

	# centrality
	# betweeness
	# community detection?

	# total 1+6+6+2+2+1 = 18 features


def calAdamic(aa, neighbor_num):
	if neighbor_num<=0:
		return aa
	elif neighbor_num==1:
		aa+=1
	else:
		aa = aa+1/math.log(neighbor_num)
	return aa

'''
Behavior
'''

def calBehaviorScore(posts1, posts2, text1, text2):
	# place sequence
	# placesSeq1 = [post["place"] for post in posts1 if post["place"]["lat"]!=0]
	# placesSeq2 = [post["place"] for post in posts2 if post["place"]["lat"]!=0]

	scores = list()
	# content
	# read the content vector for uid

	# place info 
	place_index1 = [i for i in range(len(posts1)) if posts1[i]["place"]["lat"]!=0]
	place_index2 = [i for i in range(len(posts2)) if posts2[i]["place"]["lat"]!=0]
	# place sequence
	# place_seq1 = [posts1[i]["place"] for i in place_index1]
	# place_seq2 = [posts2[i]["place"] for i in place_index2]

	place_seq1 = [(posts1[i]["place"]["lat"], posts1[i]["place"]["lng"]) for i in place_index1]
	place_seq2 = [(posts2[i]["place"]["lat"], posts2[i]["place"]["lng"]) for i in place_index2]
	# time seqeunce
	time_seq1 = [ut.parseSNTime(post["time"]) for post in posts1]
	time_seq2 = [ut.parseSNTime(post["time"]) for post in posts2]
	time_seq1, time_seq2, trim_seq, trim_index = getSamePeriodTime(time_seq1, time_seq2)
	# post sequence include place and time
	post_with_place_index1 = list()
	post_with_place_index2 = list()
	if trim_seq==1:
		post_with_place_index1 = [index for index in place_index1 if index < trim_index]
	elif trim_seq==2:
	 	post_with_place_index2 = [index for index in place_index2 if index < trim_index]
	scores = calContentScore(text1, text2)+calSpatialScore(place_seq1, place_seq2)+ calTemporalScore(time_seq1, time_seq2, post_with_place_index1, post_with_place_index2, posts1, posts2)
	# temporal include spatial temporal and content temporal feature
	return scores


# Return: tf_top_sim, tf_top5_sim, tfidf_top5_sim, cosine_sim, lang_sim, lang_d, sentiment_sim
def calContentScore(text1, text2):
	tf_top_sim = int()
	tf_top5_sim = float()
	tfidf_top5_sim = float()
	cosine_sim = float()
	lang_sim = float()
	lang_d = float()
	sentiment_sim = float()
	topic_sim = float()

	# tf, idf, cosine
	# tf_top5_1 = text1["tf_top5"]
	# tf_top5_2 = text2["tf_top5"]
	tf_top5_1 = [t[0] for t in text1["tf_top5"]]
	tf_top5_2 = [t[0] for t in text2["tf_top5"]]
	if len(tf_top5_1)==0 or len(tf_top5_2)==0:
		return [0]*7
	else:
		tfidf_top5_1 = [t[0] for t in text1["tfidf_top5"]]
		tfidf_top5_2 = [t[0] for t in text2["tfidf_top5"]]
		if tf_top5_1[0] == tf_top5_2[0]:
			tf_top_sim = 1
		else:
			tf_top_sim = 0
		tf_top5_sim = jaccard(tf_top5_1, tf_top5_2)
		tfidf_top5_sim = jaccard(tfidf_top5_1, tfidf_top5_2)
		cosine_sim = cosine(text1["tfidf"], text2["tfidf"])

		# lang
		if text1["lang"] == text2["lang"]:
			lang_sim = 1
		else:
			lang_sim = 0
		# lang divergence
		lang_d = calKLDivergence(text1["lang_distri"], text2["lang_distri"])
		sentiment_sim = 1 - abs(text1["sentiment"]-text2["sentiment"])
		topic_d = calKLDivergence(text1["topic_distri"], text2["topic_distri"])
		return [tf_top_sim, tf_top5_sim, tfidf_top5_sim, cosine_sim, lang_sim, lang_d, sentiment_sim, topic_d]

# Input: places with point 2 accuracy
def calSpatialScore(place_seq1, place_seq2):
	scores = list()
	if len(place_seq1)==0 or len(place_seq2)==0:
		return [0]*4
	places1 = set(place_seq1)
	places2 = set(place_seq2)
	place_num1 = ut.getDistri(place_seq1)
	place_num2 = ut.getDistri(place_seq2)

	# 如果到小數點後第二位一樣就算是同一個地方
	# most visited place
	most_visited_places1 = [place for place, num in place_num1.items() if num==max(place_num1, key=place_num1.get)]
	most_visited_places2 = [place for place, num in place_num2.items() if num==max(place_num2, key=place_num2.get)]
	mvp = 1 if len(set(most_visited_places1)and set(most_visited_places2))>0 else 0
	# common place 
	cp = len(places1 and places2)/len(places1 or places2)
	# place divergence
	pd = calKLDivergence(place_num1, place_num2)
	# average distance ratio
	avg_distance1 = float()
	avg_distance2 = float()
	if len(places1) ==1 or len(places2) == 1:
		avgdRatio = 1
	else:
		for p1 in places1:
			for p2 in places1:
				avg_distance1+= calDistance(p1, p2)
		for p1 in places2:
			for p2 in places2:
				avg_distance2+= calDistance(p1, p2)
		avg_distance1/=(len(places1)*(len(places1)-1))/2
		avg_distance2/=(len(places2)*(len(places2)-1))/2
		avgdRatio = max(avg_distance1, avg_distance2)/min(avg_distance1, avg_distance2)
	scores = [mvp, cp, pd, avgdRatio]
	return scores


# can be accelerated by just one loop
def calTemporalScore(times1, times2, post_with_place_index1, post_with_place_index2, posts1, posts2):
	scores = list()
	mins1 = list()
	hrs1 = list()
	days1 = list()
	weeks1 = list()
	mons1 = list()
	by_hr1 = list()
	by_mon1= list()
	mins2 = list()
	hrs2 = list()
	days2 = list()
	weeks2 = list()
	mons2 = list()
	by_hr2 = list()
	by_mon2 = list()

	# temporal features
	if len(times1)>0 and len(times2)<=0:
		return [0]*15
	# times1 and times2
	for t in times1:
		mins1.append(str(t.tm_year)+str(t.tm_yday)+str(t.tm_hour)+str(int(t.tm_min)/10))
		hrs1.append(str(t.tm_year)+str(t.tm_yday)+str(t.tm_hour))
		days1.append(str(t.tm_year)+str(t.tm_yday))
		weeks1.append(str(t.tm_year)+str(int(t.tm_yday)/7))
		mons1.append(str(t.tm_year)+str(t.tm_mon))
		by_hr1.append(str(t.tm_hour))
		by_mon1.append(str(t.tm_mon))
	for t in times2:
		mins2.append(str(t.tm_year)+str(t.tm_yday)+str(t.tm_hour)+str(int(t.tm_min)/10))
		hrs2.append(str(t.tm_year)+str(t.tm_yday)+str(t.tm_hour))
		days2.append(str(t.tm_year)+str(t.tm_yday))
		weeks2.append(str(t.tm_year)+str(int(t.tm_yday)/7))
		mons2.append(str(t.tm_year)+str(t.tm_mon))
		by_hr2.append(str(t.tm_hour))
		by_mon2.append(str(t.tm_mon))

	td_10min = calKLDivergence(ut.getDistri(mins1), ut.getDistri(mins2))
	td_hr = calKLDivergence(ut.getDistri(hrs1), ut.getDistri(hrs2))
	td_day = calKLDivergence(ut.getDistri(days1), ut.getDistri(days2))
	td_week = calKLDivergence(ut.getDistri(weeks1), ut.getDistri(weeks2))
	td_mon = calKLDivergence(ut.getDistri(mons1), ut.getDistri(mons2))
	td_by_hr = calKLDivergence(ut.getDistri(by_hr1), ut.getDistri(by_hr2))
	td_by_mon = calKLDivergence(ut.getDistri(by_mon1), ut.getDistri(by_mon2))

	# spatial temporal features
	temp_spatial1_hr, temp_spatial1_day, temp_spatial1_week, temp_spatial1_by_hr, temp_spatial1_by_mon = temp_spatial_distri(posts1, post_with_place_index1, weeks1, days1, hrs1, by_hr1, by_mon1)
	temp_spatial2_hr, temp_spatial2_day, temp_spatial2_week, temp_spatial2_by_hr, temp_spatial2_by_mon = temp_spatial_distri(posts2, post_with_place_index2, weeks2, days2, hrs2, by_hr2, by_mon2)

	cp_hr = temp_spatial_common_place(temp_spatial1_hr, temp_spatial2_hr)
	cp_day = temp_spatial_common_place(temp_spatial1_day, temp_spatial2_day)
	cp_mon = temp_spatial_common_place(temp_spatial1_week, temp_spatial2_week)
	cp_by_hr = temp_spatial_common_place(temp_spatial1_by_hr, temp_spatial2_by_hr)
	cp_by_mon = temp_spatial_common_place(temp_spatial1_by_mon, temp_spatial2_by_mon)
	pd_by_hr = temp_spatial_divergence(temp_spatial1_by_hr, temp_spatial2_by_hr, 24)
	pd_by_mon = temp_spatial_divergence(temp_spatial1_by_mon, temp_spatial2_by_mon, 24)
	avgd_hr = temp_spatial_distance(temp_spatial1_hr, temp_spatial2_hr)

	# content temporal features: sentiment and topic comparison
	temp_sentiment1_hr, temp_sentiment1_day, temp_sentiment1_week, temp_sentiment1_mon = temp_sentiment_distri(posts1, mons1, weeks1, days1, hrs1)
	temp_sentiment2_hr, temp_sentiment2_day, temp_sentiment2_week, temp_sentiment2_mon = temp_sentiment_distri(posts2, mons2, weeks2, days2, hrs2)
	temp_topic_distri1_hr ,temp_topic_distri1_day, temp_topic_distri1_week, temp_topic_distri1_mon = temp_topic_distri(posts1, mons1, weeks1, days1)
	temp_topic_distri2_hr, temp_topic_distri2_day, temp_topic_distri2_week, temp_topic_distri2_mon = temp_topic_distri(posts2, mons2, weeks2, days2)


	senti_sim_hr = calTempSentimentSim(temp_sentiment1_hr, temp_sentiment2_hr)
	senti_sim_day = calTempSentimentSim(temp_sentiment1_day, temp_sentiment2_day)
	senti_sim_week = calTempSentimentSim(temp_sentiment1_week, temp_sentiment2_week)
	senti_sim_mon = calTempSentimentSim(temp_sentiment1_mon, temp_sentiment2_mon)

	topic_d_day = calTempTopicDivergence(temp_topic_distri1_day, temp_topic_distri2_day)
	topic_d_week = calTempTopicDivergence(temp_topic_distri1_week, temp_topic_distri2_week)
	topic_d_mon = calTempTopicDivergence(temp_topic_distri1_mon, temp_topic_distri2_mon)

	# all scores 
	scores_temp = [td_10min, td_hr, td_day, td_week, td_mon, td_by_hr, td_by_mon]
	scores_spatial_temp = [cp_hr, cp_day, cp_mon, cp_by_hr, cp_by_mon, pd_by_hr, pd_by_mon, avgd_hr]
	scores_content_temp = [senti_sim_hr, senti_sim_day, senti_sim_week, senti_sim_mon, topic_d_day, topic_d_week, topic_d_mon]

	scores = scores_temp + scores_spatial_temp
	return scores


def calTempTopicDivergence(temp_topic_distri1, temp_topic_distri2):
	count = 0
	total = 0.0
	for key, distri in temp_topic_distri1.items():
		if key in temp_topic_distri2:
			total += calKLDivergence(distri, temp_topic_distri2[key])
			count += 1
	if count == 0:
		return 0
	else:
		return total/count

def calTempSentimentSim(temp_sentiment1, temp_sentiment2):
	count = 0
	total = 0.0
	for key, value in temp_sentiment1.items():
		if key in temp_sentiment2:
			total = 1-abs(value, temp_sentiment2[key])
			count += 1
	if count==0:
		return 0
	else:
		return total/count



def temp_sentiment_distri(posts, mons, weeks, days, hrs):
	temp_sentiment_hr = dict()
	temp_sentiment_day = dict()
	temp_sentiment_week = dict()
	temp_sentiment_mon = dict()

	for i in range(len(posts)):
		sentiment = posts[i]["sentiment"]["polarity"]
		if sentiment != 0:
			temp_sentiment_a_hr = temp_sentiment_hr.get(hrs[i], list())
			temp_sentiment_a_day = temp_sentiment_day.get(days[i], list())
			temp_sentiment_a_week = temp_sentiment_week.get(weeks[i], list())
			temp_sentiment_a_mon = temp_sentiment_mon.get(mons[i], list())

			temp_sentiment_a_hr.append(sentiment)
			temp_sentiment_a_day.append(sentiment)
			temp_sentiment_a_week.append(sentiment)
			temp_sentiment_a_mon.append(sentiment)

			temp_sentiment_hr[hrs[i]] = temp_sentiment_a_hr
			temp_sentiment_day[days[i]] = temp_sentiment_a_day
			temp_sentiment_week[weeks[i]] = temp_sentiment_a_week
			temp_sentiment_mon[mons[i]] = temp_sentiment_a_mon
	temp_sentiment_hr = ut.avgDict(temp_sentiment_hr)
	temp_sentiment_day = ut.avgDict(temp_sentiment_day)
	temp_sentiment_week = ut.avgDict(temp_sentiment_week)
	temp_sentiment_mon = ut.avgDict(temp_sentiment_mon)
	return temp_sentiment_hr, temp_sentiment_day, temp_sentiment_week, temp_sentiment_mon


def temp_topic_distri(posts, mons, weeks, days):
	temp_topic_distri_hr = dict()
	temp_topic_distri_day = dict()
	temp_topic_distri_week = dict()
	temp_topic_distri_mon = dict()
	for i in range(len(posts)):
		topic_distri = posts[i]["topic_distri"]
		if len(topic_distri) > 0:
			temp_topic_distri_a_hr = temp_topic_distri_hr.get(hrs[i], dict())
			temp_topic_distri_a_day = temp_topic_distri_day.get(days[i], dict())
			temp_topic_distri_a_week = temp_topic_distri_week.get(weeks[i], dict())
			temp_topic_distri_a_mon = temp_topic_distri_mon.get(mons[i], dict())
			temp_topic_distri_hr[hrs[i]] = ut.addDict(temp_topic_distri_a_hr, topic_distri)
			temp_topic_distri_day[days[i]] = ut.addDict(temp_topic_distri_a_day, topic_distri)
			temp_topic_distri_week[weeks[i]] = ut.addDict(temp_topic_distri_a_week, topic_distri)
			temp_topic_distri_mon[mons[i]] = ut.addDict(temp_topic_distri_a_mon, topic_distri)

	temp_topic_distri_hr = ut.normVectorDict(temp_topic_distri_hr)
	temp_topic_distri_day = ut.normVectorDict(temp_topic_distri_day)
	temp_topic_distri_week = ut.normVectorDict(temp_topic_distri_week)
	temp_topic_distri_mon = ut.normVectorDict(temp_topic_distri_mon)
	return temp_topic_distri_hr, temp_topic_distri_day, temp_topic_distri_week, temp_topic_distri_mon




# Description: Place set in every time slot
def temp_spatial_distri(posts, post_with_place_index, weeks, days, hrs, by_hr, by_mon):
	temp_spatial_hr = dict()
	temp_spatial_day = dict()
	temp_spatial_week = dict()
	temp_spatial_by_hr = dict()
	temp_spatial_by_mon = dict()
	for index in post_with_place_index:
		# place = posts[index]["place"]
		place = (posts[index]["place"]["lat"], posts[index]["place"]["lng"])
		temp_spatial_hr_index = temp_spatial_hr.get(hrs[index], set())
		temp_spatial_day_index = temp_spatial_day.get(days[index], set())
		temp_spatial_week_index = temp_spatial_week.get(weeks[index], set())
		temp_spatial_by_hr_index = temp_spatial_by_hr.get(by_hr[index], list())
		temp_spatial_by_mon_index = temp_spatial_by_mon.get(by_mon[index], list())

		temp_spatial_hr_index.add(place)
		temp_spatial_day_index.add(place)
		temp_spatial_week_index.add(place)
		temp_spatial_by_hr_index.append(place)
		temp_spatial_by_mon_index.append(place)

		temp_spatial_hr[hrs[index]] = temp_spatial_hr_index
		temp_spatial_day[days[index]] = temp_spatial_day_index
		temp_spatial_week[weeks[index]] = temp_spatial_week_index
		temp_spatial_by_hr[by_hr[index]] = temp_spatial_by_hr_index
		temp_spatial_by_mon[by_mon[index]] = temp_spatial_by_mon_index
	return temp_spatial_hr, temp_spatial_day, temp_spatial_week, temp_spatial_by_hr, temp_spatial_by_mon


def temp_spatial_distance(temp_spatial_set1, temp_spatial_set2):
	avgd = 0
	count = int()
	for t, set1 in temp_spatial_set1.items():
		set2 = temp_spatial_set2.get(t, set())
		if len(set2) != 0:
			for place1 in set1:
				for place2 in set2:
					avgd+=calDistance(place1, place2)
					count+=1
	if count == 0:
		return 0
	else:
		avgd /= count
		return avgd

# Description: calculate the place divergence in a time period
def temp_spatial_divergence(temp_spatial_list1, temp_spatial_list2, total):
	pd = float()
	for t in temp_spatial_list1:
		pd+= calKLDivergence(ut.getDistri(temp_spatial_list1[t]), ut.getDistri(temp_spatial_list2.get(t, list())))
	return pd/total


# Description: calculate the common place ratio through time
def temp_spatial_common_place(temp_spatial_set1, temp_spatial_set2):
	cp = float()
	if len(temp_spatial_set1) ==0 or len(temp_spatial_set2)==0:
		return 0
	else:
		for t in temp_spatial_set1:
			place_set1 = set(temp_spatial_set1[t])
			place_set2 = set(temp_spatial_set2.get(t, set()))
			if len(place_set2) != 0:
				cp += (place_set1 and place_set2) / (place_set1 or place_set2)
		cp /= len(set(temp_spatial_set1.keys()) and set(temp_spatial_set2.keys()))
		return cp









'''
Others
'''

def cosine(dict1, dict2):
	cosine = float()
	for key, value in dict1.items():
		cosine += dict2.get(key, 0) * value
	return cosine


def jaccard(list1, list2):
	set1 = set(list1)
	set2 = set(list2)
	return len(set1.intersection(set2))/len(set1.union(set2))


# def detectTopic(sentence):

def checkSamePlace(place1, place2):
	# if round(place1["lat"],2)==round(place2["lat"],2) and round(place1["lng"],2)==round(place2["lng"],2):
	if round(place1[0],2)==round(place2[0],2) and round(place1[1],2)==round(place2[1],2):
		return True
	else:
		return False

# Input: {"lat":1, "lng":1}
# Return: distance
def calDistance(place1, place2):
	# return math.sqrt(math.pow(place1["lat"]-place2["lat"], 2)+math.pow(place1["lng"]-place2["lng"], 2))
	return math.sqrt(math.pow(place1[0]-place2[0], 2)+math.pow(place1[1]-place2[1], 2))


def calKLDivergence(distri1, distri2):
	kl1 = float()
	kl2 = float()
	if len(distri1) == 0 or len(distri2)==0:
		return 1
	for key1, value1 in distri1.items():
		value2 = distri2.get(key1, 0.00000001)
		value1 = float(value1)
		kl1 += value1 * math.log(value1/value2, math.e)
	for key2, value2 in distri2.items():
		value1 = distri1.get(key2, 0.00000001)
		value2 = float(value2)
		kl2 += value2 * math.log(value2/value1, math.e)
	return (kl1+kl2)/2

def getSamePeriodTime(times1, times2):
	if len(times1) >0 and len(times2)>0:
		# times2 is earlier
		if (time.mktime(times1[-1])-time.mktime(times2[-1]))>0:
			timeStart = time.mktime(times1[-1])
			for i in range(len(times2)-1, -1, -1):
				if time.mktime(times2[i]) - timeStart >= 0:
					times2 = times2[:i+1]
					break
			return times1, times2, 2, len(times2)
		else:
			timeStart = time.mktime(times2[-1])
			for i in range(len(times1)-1, -1, -1):
				if time.mktime(times1[i]) - timeStart >= 0:
					times1 = times1[:i+1]
					break
			return times1, times2, 1, len(times1)
	else:
		return times1, times2, 0, 0

def readMostPopularCount():
	# mpCount = ut.readJson2Dict(interPath, popularCountFileName)
	mpCount= {"google":1, "twitter": 1}
	return mpCount

def writeMostPopularCount(g1, sn1, users_sn1, g2, sn2, users_sn2):
	in_degree_sn1 = list()
	in_degree_sn2 = list()
	for user in users_sn1:
		in_degree_sn1.append(g1.in_degree(user))
	for user in users_sn2:
		in_degree_sn2.append(g2.in_degree(user))
	result = {sn1:max(in_degree_sn1), sn2:max(in_degree_sn2)}
	ut.writeDict2Json(interPath, popularCountFileName, result)
	# result = [[sn1, "1"], [sn2, "1"]]
	# ut.writeList2CommaLine(interPath, popularCountFileName, result)

def getFeatureStr(rank, uid1, uid2, scores):
	featureStr = str(rank)+" qid:"+uid1
	for i in range(len(scores)):
		score = scores[i]
		featureStr += " " + str(i+1)+":"+str(score)
	featureStr += " # "+uid2+"\n"
	return featureStr

def getPairFeatures():
	pairFeatures = dict()
	with open(outputPath+featureFileNamePrevious, "r") as fi:
		for line in fi:
			tmp = line.split("#")
			uid2 = tmp[1].strip()
			matches = re.match(r"\d+ qid:(\d+) ([\w\.: ]*)", tmp[0])
			# print(matches)
			uid1 = matches.group(1)
			featureStr = matches.group(2).strip()
			pairFeatures[(uid1, uid2)] = featureStr
	return pairFeatures



if __name__ == "__main__":
	getUsersFeatures()

	# getBehaviorScore("google", "109174551750397653742", "twitter", "nickbilton")
	# getBehaviorScore("google", "117232298690269038526", "twitter", "joyyang1103")
	# getBehaviorScore("google", "110356488025922357921", "twitter", "evenchange4")
	# getBehaviorScore("google", "116663982997041117781", "twitter", "hunterwalk")



	# testing
	# print(getProfileScore("google", "109174551750397653742", "twitter", "nickbilton"))
	# print(getProfileScore("google", "109174551750397653742", "twitter", "nickbilton"))
