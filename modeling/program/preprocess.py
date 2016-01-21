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
gtFileName = "gt"
sn1 = "google"
sn2 = "twitter"
twitterNameIdFileName = "twitterNameId"

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
	twitterNameId = ut.readJson2Dict(interPath, twitterNameIdFileName)
	gts = ut.readCommaLine2List(interPath, gtFileName)
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
				uid1 = twitterNameId[uid1]
			if sn2 =="twitter":
				uid2 = twitterNameId[uid2]
		except:
			continue
		if not os.path.exists(interPath+sn1+"/profile/"+uid1):
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
	print("profile:"+interPath+sn+"/profile/"+uid)
	profile = ut.readJson2Dict(inputPath+sn+"/profile/", uid)
	newProfile = normProfile(sn, profile)
	ut.writeDict2Json(interPath+sn+"/profile/", uid, newProfile)

	# norm wall
	print("wall:"+interPath+sn+"/wall/"+uid)
	posts = ut.readJson2Dict(inputPath+sn+"/wall/", uid)
	newPosts = normWall(sn, posts)
	# normwall too long
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
	profile["displayName"] = jresult["displayName"].lower().strip()
	profile["placesLived"] = jresult["placesLived"]
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
			if page_count >10:
				# revise the size in the future
				break
			for post in page["items"]:
				# a = time.time()
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
	ut.writeList2Line(interPath, "dictionary.txt", sorted(idf.keys()))
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





# Input: google social network mapping
# Output: youtube mapping file, facebook mapping file, twitter mapping file
# Description: revise ground truth by twitter profile and google plus profile
def reviseGroundTruth():
	mapping = ut.readCommaLine2List(inputPath, mappingFileName)
	fmapping = list()
	twitterNameId = dict()
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
			location = "../data/twitter/profile/"+twitterName
			with open(location, "r") as fi:
				jresult = json.loads(fi.read())
				id_str = jresult.get("id_str", 0)
				if id_str != 0:
					fmapping.append([m[0], id_str])
					twitterNameId[id_str] = twitterName
				else:
					print(jresult)
		except:
			pass
	ut.writeList2CommaLine(interPath, "gt", fmapping)
	ut.writeDict2Json(interPath, "twitterNameId", twitterNameId)


def reviseTwitterNameId():
	names = list()
	# read name id mapping
	twitterNameId = ut.readJson2Dict(interPath, "twitterNameId")
	# replace the name by id and write file
	with open(inputPath+"twitter/relationship_file_revise", "w") as fo:
		with open(inputPath+"twitter/relationship_file", "r") as fi:
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
	# reviseGroundTruth()

	# revise twitter relationship file for id
	# reviseTwitterNameId()

	structData()