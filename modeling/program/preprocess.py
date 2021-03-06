# Description: this file is for structure the data from every social network
import os
import multiprocessing as mp
import utility as ut
import json
import langid
from textblob import TextBlob
from nltk.corpus import stopwords as sw
import time
import math
import operator


inputPath = "../data/"
interPath = "../intermediate/"
outputPath = '../output/'

mappingFileName = "twitterMapping"
mappingLossFileName = "gt_loss"
gtLooseFileName = "gt_loose"
gtStrictFileName = "gt_strict"
sn1 = "google"
sn2 = "twitter"
twitterNameIdFileName = "twitterNameId"
twitterIdNameFileName = "twitterIdName"

stopwords = sw.words("english")
'''
Struct Data Main Function
'''

# Description: main function to structure the users' profile and wall
def structData():
	# init
	s = time.time()
	usersTf1 = dict()
	usersTf2 = dict()
	usersLangDistri1 = dict()
	usersLangDistri2 = dict()
	usersSentimentScore1 = dict()
	usersSentimentScore2 = dict()
	usersTopicDistir1 = dict()
	usersTopicDistri2 = dict()
	twitterIdName = ut.readJson2Dict(interPath, twitterIdNameFileName)
	gts_loose = ut.readCommaLine2List(interPath, gtLooseFileName)
	gts_strict = ut.readCommaLine2List(interPath, gtStrictFileName)
	gts = gts_strict
	if not os.path.isdir(interPath+sn1):
		os.makedirs(interPath+sn1+"/profile")
		os.makedirs(interPath+sn1+"/wall")
		os.makedirs(interPath+sn1+"/text")
		os.makedirs(interPath+sn2+"/profile")
		os.makedirs(interPath+sn2+"/wall")
		os.makedirs(interPath+sn2+"/text")
	# norm profile and wall
	for gt in gts:
		uid1 = gt[0]
		uid2 = gt[1]
		try:
			if sn1 == "twitter":
				uid1 = twitterIdName[uid1]
			if sn2 =="twitter":
				uid2 = twitterIdName[uid2]
		except:
			continue
		# if not os.path.exists(interPath+sn1+"/profile/"+uid1):
			# norm profile and posts: google and twitter
		(userTf1, langDistri1, userSentimentScore1, userTopicDistri1) = structUserData(sn1, uid1)
		(userTf2, langDistri2, userSentimentScore2, userTopicDistri2) = structUserData(sn2, uid2)
		usersTf1[uid1] = userTf1 
		usersTf2[uid2] = userTf2
		usersLangDistri1[uid1] = langDistri1
		usersLangDistri2[uid2] = langDistri2
		usersSentimentScore1[uid1] = userSentimentScore1
		usersSentimentScore2[uid2] = userSentimentScore2
		usersTopicDistir1[uid1] = userTopicDistri1
		usersTopicDistri2[uid2] = userTopicDistri2
	# build dictionary and idf
	writeStatWalls(usersTf1, usersTf2, usersLangDistri1, usersLangDistri2, usersSentimentScore1, usersSentimentScore2, usersTopicDistir1, usersTopicDistri2)
	e = time.time()
	print(e-s)


# Description: For one user, write the normalized profile and wall and return wall statistics
# Input: social network user id
# Return: statisitic for the content of the user
def structUserData(sn, uid):
	print(uid)
	# norm profile
	profile = ut.readJson2Dict(inputPath+sn+"/profile/", uid)
	posts = ut.readJson2Dict(inputPath+sn+"/wall/", uid)

	print("profile:"+interPath+sn+"/profile/"+uid)
	newProfile = normProfile(sn, profile)
	print("wall:"+interPath+sn+"/wall/"+uid)
	newPosts = normWall(sn, posts)

	ut.writeDict2Json(interPath+sn+"/profile/", uid, newProfile)
	ut.writeDict2Json(interPath+sn+"/wall/", uid, newPosts)

	# wall statisitcs
	langDistri = ut.getDistri([post["lang"] for post in newPosts])
	# sentiment sum
	sentiments = [post["sentiment"]["polarity"] for post in newPosts]
	sentiment_score = sum(sentiments)/len(sentiments) if len(sentiments)>0 else 0
	# topic sum
	topicDistris = [post["topic_distri"] for post in newPosts]
	userTopicDistri = ut.mergeDict(topicDistris)
	userTopicDistri = ut.normVector(userTopicDistri)
	# tf
	tfs = [post["tf"] for post in newPosts]
	userTf = ut.mergeDict(tfs)
	return (userTf, langDistri, sentiment_score, userTopicDistri)


'''
Profile
'''
def normProfile(sn, jresult):
	if sn=="twitter":
		return normTwitterProfile(jresult)
	else:
		return normGoogleProfile(jresult)

def normTwitterProfile(jresult):
	# location, name, screen_name, lang, followers_count, description
	profile = dict()
	profile["name"] = jresult["name"].lower().strip()
	profile["displayName"] = jresult["screen_name"].lower().strip()
	profile["placesLived"] = [{"value": jresult["location"], "primary": True}]
	profile["circledByCount"] = jresult.get("followers_count", 0)
	profile["tags"] = getStringTag(jresult["description"])
	profile["nameLang"] = ut.detectLang(profile["name"])
	profile["displayNameLang"] = ut.detectLang(profile["displayName"])
	# print(profile)
	return profile

def normGoogleProfile(jresult):
	# placesLived(value, primary), name(givenName, familyName), displayName, circledByCount, occupation, aboutMe, organizations(name, title, endDate, startDate), gender
	profile = dict()
	profile["name"] = (jresult["name"]["givenName"]+" "+jresult["name"]["familyName"]).lower().strip()
	profile["displayName"] = jresult.get("displayName","").lower().strip()
	profile["placesLived"] = jresult.get("placesLived", list())
	profile["circledByCount"] = jresult.get("circledByCount", 0)
	profile["tags"] = getGoogleTag(jresult)
	profile["nameLang"] = ut.detectLang(profile["name"])
	profile["displayNameLang"] = ut.detectLang(profile["displayName"])
	return profile


def getGoogleTag(jresult):
	string = str()
	gender = jresult.get("gender", "")
	tagline = jresult.get("tagline", "")
	relationship = jresult.get("relationshipStatus", "")
	skills = jresult.get("skills","")
	# bragging = jresult.get("braggingRights", "")
	aboutMe = jresult.get("aboutMe", "")
	occupation = jresult.get("occupation", "")
	string = gender+" "+tagline+" "+relationship+" "+skills+" "+aboutMe+" "+occupation
	organizations = jresult.get("organizations", "")
	if organizations != "":
		for organization in organizations:
			string += " "+organization.get("title","")+" "+organization.get("name","")
	tags = getStringTag(string)
	return tags


def getStringTag(string):
	tokens = list(ut.wordProcess(string, ut.detectLang(string)).keys())
	return tokens
'''
Wall
'''
# make the text to tf dictionary and tf-idf dictionary: for most used words, and 
def normWall(sn, jresult):
	if sn == "twitter":
		return normTwitterWall(jresult)
	else:
		return normGoogleWall(jresult)

def normTwitterWall(wall):
	posts = list()
	for post in wall:
		text = post.get("text", "")
		time = formatTwitterTime(post.get("created_at"))
		place = formatTwitterPlace(post["geo"], 2)
		urls = getTwitterUrls(post)
		lang = post.get("lang", "")
		if lang == "":
			lang = ut.detectLang(text)
		# translate text
		text_en = ut.translate(text, lang)
		sentiment = ut.getSentiment(text_en)
		topic_distri = ut.getTopic(text_en)
		tf = ut.wordProcess(text, lang)
		posts.append(getPost(text, text_en, time, place, urls, lang, sentiment, topic_distri, tf))
	return posts


def normGoogleWall(jresult):
	posts = list()
	page_count = 0
	if type(jresult) == list:
		for page in jresult:
			if page_count > 10:
				# revise the size in the future
				break
			for post in page["items"]:
				published_time = formatGoogleTime(post["published"])
				place = formatGooglePlace(post.get("location", ""), 2)
				info = post.get("object", "")
				if info != "":
					text = info.get("content", "")
					urls = getGoogleUrls(info.get("attachments", ""))
					# a = time.time()
					lang = ut.detectLang(text)
					# b = time.time()
					text_en = ut.translate(text, lang)
					# c= time.time()
					sentiment = ut.getSentiment(text_en)
					# d= time.time()
					topic_distri = ut.getTopic(text_en)
					tf = ut.wordProcess(text, lang)
					# e= time.time()
					# print(b-a, c-b, d-c, e-d)
					posts.append(getPost(text, text_en, published_time, place, urls, lang, sentiment, topic_distri, tf))
			page_count+=1
	return posts


def formatTwitterPlace(geo, num):
	place = dict()
	if geo != None and geo != "null":
		place["lat"] = round(geo["coordinates"][0], num)
		place["lng"] = round(geo["coordinates"][1], num)
	else:
		place["lat"] = 0
		place["lng"] = 0
	return place


def formatGooglePlace(location, num):
	place = dict()
	place["lat"] = 0
	place["lng"] = 0
	if location != None and location!= "":
		position = location.get("position",0)
		if position != 0:
			place["lat"] = round(position.get("latitude"), num)
			place["lng"] = round(position.get("longitude"), num)
	return place


def formatTwitterTime(time_str):
	t = time.strptime(time_str, "%a %b %d %H:%M:%S +0000 %Y")
	return time.strftime("%Y-%m-%dT%H:%M:%S", t)

def formatGoogleTime(time_str):
	return time_str.split(".")[0]

def getTwitterUrls(post):
	urls = list()
	entities = post["entities"]
	medias = entities.get("media", 0)
	if medias != 0:
		for media in medias:
			url = media.get("media_url", "")
			if  url != "":
				urls.append(url)
	urlModules = entities.get("urls", 0)
	if urlModules != 0:
		for urlModule in urlModules:
			url = urlModule.get("expanded_url", "")
			if url != "":
				urls.append(url)
	urlLink = entities.get("url", 0)
	if urlLink != 0:
		for u in urlLink["urls"]:
			url = u.get("expanded_url",0)
			if url != 0:
				urls.append(url)
	return urls

def getGoogleUrls(attachments):
	urls = list()
	if attachments != "":
		for attachment in attachments:
			url = attachment.get("url", "")
			image = attachment.get("image", "")
			if url !="":
				urls.append(url)
			if image != "":
				url = image.get("url", "")
				if url != "":
					urls.append(url)
	return urls


def getPost(text, text_en, time, place, urls, lang, sentiment, topic_distri, tf):
	post = dict()
	post["text"] = text
	post["text_en"] = text_en
	post["time"] = time
	post["place"] = place
	post["urls"] = urls
	post["lang"] = lang
	post["sentiment"] = sentiment
	post["topic_distri"] = topic_distri
	post["tf"] = tf
	return post

# def normGoogleWall(jresult):



'''
Revise Data
'''

def writeStatWalls(usersTf1, usersTf2, usersLangDistri1, usersLangDistri2, usersSentimentScore1, usersSentimentScore2, usersTopicDistri1, usersTopicDistri2):
	# build dictionary and idf
	idf = dict()
	for user, tf in usersTf1.items():
		for term in tf:
			idf[term] = idf.get(term, 0) +1
	for user, tf in usersTf2.items():
		for term in tf:
			idf[term] = idf.get(term, 0) +1
	n = len(usersTf1) * 2
	for term, df in idf.items():
		idf[term] = math.log(n/df)
	# write dictionary
	ut.writeDict2Json(interPath, "idf.json", idf)
	ut.writeList2Json(interPath, "dictionary.txt", sorted(idf.keys()))
	# write unit vector
	writeTextStat(usersTf1, usersLangDistri1, idf, sn1, usersSentimentScore1, usersTopicDistri1)
	writeTextStat(usersTf2, usersLangDistri2, idf, sn2, usersSentimentScore2, usersTopicDistri2)

# Text statistics includes tfidf and language in text
def writeTextStat(usersTf, usersLangDistri, idf, sn, usersSentimentScore, usersTopicDistri):
	for user, tf in usersTf.items():
		tf_top5 = list()
		tfidf_top5 = list()
		result = dict()
		norm = float()
		result["tf_top5"] = sorted(tf.items(), key=operator.itemgetter(1), reverse=True)[:5]
		for term, fre in tf.items():
			usersTf[user][term] = fre * idf[term]
			norm += math.pow(usersTf[user][term], 2)
		# unit vector
		norm = math.sqrt(norm)
		for term in tf.keys():
			usersTf[user][term] = usersTf[user][term]/norm
		result["tfidf_top5"] = sorted(usersTf[user].items(), key=operator.itemgetter(1), reverse=True)[:5]
		result["tfidf"] = usersTf[user]
		result["lang_distri"] = usersLangDistri[user]
		if len(result["lang_distri"])>0:
			result["lang"] = max(usersLangDistri[user].items(), key=operator.itemgetter(1))[0]
		else:
			result["lang"] = "none"
		result["sentiment"] = usersSentimentScore[user]
		result["topic_distri"] = usersTopicDistri[user]
		ut.writeDict2Json(interPath+sn+"/text",user,result)


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


# Input: google social network mapping
# Output: gt(google, twitter mapping), and twitternameid, twitteridname (twitter name id mapping file)
# Description: Get the ground truth mapping of loose and strict mode
def getGroundTruth():
	mapping = ut.readCommaLine2List(inputPath, mappingFileName)
	mappingIdLoose = list()
	mappingIdStrict = list()
	twitterNameId = dict()
	twitterIdName = dict()
	mappingLoss = list()
	for m in mapping:
		twitterUrl = m[1]
		twitterName = getTwitterUsername(twitterUrl)
		googleId = m[0]

		if twitterName == "":
			continue
		(google_profile_bool, google_posts_bool) = checkGoogleData(googleId)
		(twitter_profile_bool, twitter_posts_bool, twitter_profile) = checkTwitterData(twitterName)

		if google_profile_bool == False or twitter_profile_bool == False:
			mappingLoss.append(m)
		else:
			twitterId = twitter_profile.get("id_str", 0)
			if google_posts_bool == False or twitter_posts_bool == False:
				mappingIdLoose.append([googleId, twitterId])
			else:
				mappingIdLoose.append([googleId, twitterId])
				mappingIdStrict.append([googleId, twitterId])
			twitterIdName[twitterId] = twitterName
			twitterNameId[twitterName] = twitterId
	ut.writeList2CommaLine(interPath, gtLooseFileName, mappingIdLoose)
	ut.writeList2CommaLine(interPath, gtStrictFileName, mappingIdStrict)
	ut.writeDict2Json(interPath, twitterNameIdFileName, twitterNameId)
	ut.writeDict2Json(interPath, twitterIdNameFileName, twitterIdName)
	ut.writeList2CommaLine(interPath, mappingLossFileName, mappingLoss)

def getTwitterUsername(url):
	username = url.split("/")[-1].strip()
	if username=="":
		username = url.split("/")[-2]
	if username=="#%21" or "twitter.com" in username:
		username = ""
	return username

def checkGoogleData(uid):
	profile = ut.readJson2Dict(inputPath+"google/profile/", uid)
	posts = ut.readJson2Dict(inputPath+"google/wall/", uid)
	profile_bool = True
	posts_bool = True
	if profile.get("status", 0) == "error" or len(profile)==0:
		profile_bool = False
	if type(posts) == dict or len(posts)==0:
		posts_bool = False
	return (profile_bool, posts_bool)

def checkTwitterData(uname):
	profile = ut.readJson2Dict(inputPath+"twitter/profile/", uname)
	posts = ut.readJson2Dict(inputPath+"twitter/wall/", uname)
	profile_bool = True
	posts_bool = True
	if len(profile)==0 or type(profile.get("errors", 0))==list:
		profile_bool = False
	if len(posts)==0:
		posts_bool = False
	return (profile_bool, posts_bool, profile)

# Input:
# Output:
# Description: revise user of the relationship_file by twitterId
def reviseTwitterRelationship():
	names = list()
	twitterNameId = ut.readJson2Dict(interPath, "twitterNameId")
	with open(interPath+"twitter/relationship_file_revise", "w") as fo:
		with open(interPath+"twitter/relationship_file", "r") as fi:
			for line in fi:
				ids = line.split(" ")
				user = ids[0]
				friends = ids[1]
				if user not in names and twitterNameId.get(user, 0) != 0:
					uid = twitterNameId[user]
					fo.write(uid+" "+friends)
				else:
					print(user)



if __name__ == "__main__":
	# revise the ground truth
	# getGroundTruth()

	# revise twitter relationship file for id
	# reviseTwitterRelationship()

	structData()