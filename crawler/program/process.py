import time
import networkx as nx
import utility as ut

snList = ["youtube", "facebook", "twitter", "linkedin", "flickr", "instagram", "tumblr", "github", "pinterest", "plus.google"]
inputPath = "../data/"
snFile = "sn_file"
twitterNameIdFileName = "twitterNameId"
twitterIdNameFileName = "twitterIdName"

'''
Create Mapping and ground truth
'''
# Input: google social network mapping
# Output: youtube mapping file, facebook mapping file, twitter mapping file
# Description: mapping files produced by google social network mapping
def createSNMapping():
	path = "../data/"
	snLists = ut.readCommaLine2List(path, snFile)
	print(len(snLists))
	fbMapping = list()
	twitterMapping = list()
	youtubeMapping = list()
	googleMapping = list()
	for snList in snLists:
		uid = snList[0]
		if snList[1] != "":
			youtubeMapping.append([snList[0],snList[1]])
		if snList[2] != "":
			fbMapping.append([snList[0],snList[2]])
		if snList[3] != "":
			twitterMapping.append([snList[0],snList[3]])
		# if "plus.google" in snList[-1]:
		# 	googleMapping.append([snList])
	print(len(twitterMapping))
	ut.writeList2CommaLine("../data", "youtubeMapping", youtubeMapping)
	ut.writeList2CommaLine("../data", "fbMapping", fbMapping)
	ut.writeList2CommaLine("../data", "twitterMapping", twitterMapping)

# Description: get the mapping candidates for crawl google and twitter profiles and walls
def writeMappingCandidates():
	mappings = ut.readCommaLine2List(inputPath, "twitterMapping")
	candidates_google = list()
	candidates_twitter = list()
	for mapping in mappings:
		google_id = mapping[0]
		twitter_url = mapping[1]
		twitter_name = getTwitterUsername(twitter_url)
		if twitter_name != "":
			candidates_google.append(google_id)
			candidates_twitter.append(twitter_name)
	ut.writeList2Line(inputPath, "google/ids_mapping", candidates_google) 
	ut.writeList2Line(inputPath, "twitter/names_mapping", candidates_twitter)

def getTwitterUsername(url):
	username = url.split("/")[-1].strip()
	if username=="":
		username = url.split("/")[-2]
	if username=="#%21" or "twitter.com" in username:
		username = ""
	return username


def getGroundTruth():
	mapping = ut.readCommaLine2List(inputPath, mappingFileName)
	mappingId = list()
	twitterNameId = dict()
	twitterIdName = dict()
	for m in mapping:
		twitterUrl = m[1]
		twitterName = twitterUrl.split("/")[-1].strip()
		googleId = m[0]
		if twitterName=="":
			twitterName = twitterUrl.split("/")[-2]
		if twitterName=="#%21" or "twitter.com" in twitterName or "twitter" == twitterName:
			continue

		# check if the google plus id is a person

		# read twitter profile file to check
		# try:
		# 	location = "../data/google/profile/"+googleId
		# 	with open(location, "r") as fi:
		# 		jresult = json.loads(fi.read())
		# 		if jresult["objectType"]!="person":
		# 			print(googleId)
		# except:
		# 	pass

		# check if the twitter name exist
		try:
			location = inputPath+"twitter/profile/"+twitterName
			with open(location, "r") as fi:
				jresult = json.loads(fi.read())
				twitterId = jresult.get("id_str", 0)
				if twitterId != 0:
					mappingId.append([googleId, twitterId])
					twitterNameId[twitterName] = twitterId
					twitterIdName[twitterId] = twitterName
		except:
			pass
	ut.writeList2CommaLine(interPath, "gt", mappingId)
	ut.writeDict2Json(interPath, twitterNameIdFileName, twitterNameId)
	ut.writeDict2Json(interPath, twitterIdNameFileName, twitterIdName)

if __name__=="__main__":
	# createSNMapping()
	writeMappingCandidates()
