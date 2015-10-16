import oauth2 as oauth
import urllib.request
import json
import utility as ut
import time
import codecs

access_token_key = "3747058694-vRq5oGRM8n1mezVe6JDYO2bqgPMMKVU0aLT0BE7"
access_token_secret = "EFuKvhM5a8Qxv4sQuPD1zSRB5svaKlg6UqdU6lh1TWmN6"
consumer_key = "9LLdHNbmo4ME2Bs0am8NQTmO2"
consumer_secret = "rBgTRk8q6UNwPrwbdirgnE1SdjC6usTuOxKuY4rN3P4FRTdvxr"
_debug = 0
oauth_token    = oauth.Token(key=access_token_key, secret=access_token_secret)
oauth_consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)
signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()
http_method = "GET"
http_handler  = urllib.request.HTTPHandler(debuglevel=_debug)
https_handler = urllib.request.HTTPSHandler(debuglevel=_debug)

path = "../data/twitter/"
allidFileName = "allid_file"
idFileName = "id_file"
idPostFileName = "id_post_file"
idProfileFileName = "id_profile_file"
idRecordFileName = "id_record_file"
profileFileName = "profile_file"
relationshipFileName = "relationship_file"
# Construct, sign, and open a twitter request
# using the hard-coded credentials above.
# friends: 1/min, profile: 12/min, post: 12/min

# Description: oauth connect before api
def twitterreq(url, method, parameters):
	req = oauth.Request.from_consumer_and_token(oauth_consumer,token=oauth_token,http_method=http_method,http_url=url, parameters=parameters)
	req.sign_request(signature_method_hmac_sha1, oauth_consumer, oauth_token)
	headers = req.to_header()
	if http_method == "POST":
		encoded_post_data = req.to_postdata()
	else:
		encoded_post_data = None
		url = req.to_url()
	opener = urllib.request.OpenerDirector()
	opener.add_handler(http_handler)
	opener.add_handler(https_handler)
	response = opener.open(url, encoded_post_data)
	return response

# Description: twitter api using example
def fetchsamples():
	# url = "https://stream.twitter.com/1/statuses/sample.json"
	url = "https://api.twitter.com/1.1/friends/ids.json?cursor=-1&user_id=3140536897&count=5000"
	parameters = []
	response = twitterreq(url, "GET", parameters)
	for line in response:
		print (line.strip())


def getUserProfile(user_id="", screen_name=""):
	url = "https://api.twitter.com/1.1/users/show.json?"
	if user_id != "":
		url = url + "&user_id="+user_id
	elif screen_name != "":
		url = url + "&screen_name="+screen_name
	else:
		return "Error"
	parameters = []
	try:
		response = twitterreq(url, "GET", parameters)
		result = response.read().decode("utf-8")
		jresult = json.loads(result)
		return jresult
	except:
		return dict()

# Description: get user profile and save it in profile
def getUsersProfile():
	# total user - crawled users before
	usernames = ut.readLine2List(path, "usernames")
	usernamesCrawled = ut.readLine2List(path, idProfileFileName)
	fi = open(path+idProfileFileName, 'a')
	for username in usernames[len(usernamesCrawled):]:
		print(username)
		time.sleep(5)
		profile = getUserProfile("",username)
		# file cannot be opened due to wrong name
		try:
			with codecs.open(path+"profile/"+username, "w", encoding="utf-8") as fo:
				fo.write(json.dumps(profile, indent=4, ensure_ascii=False))
		except:
			pass
		fi.write(username+'\n')



# Description: get max 5000 friends at a time if exceed put into friends_over1page
def getUserFriendship(id_post_writer, user_id="", screen_name=""):
	url = "https://api.twitter.com/1.1/friends/ids.json?cursor=-1&count=5000"
	if user_id != "":
		url = url + "&user_id="+user_id
	elif screen_name != "":
		url = url + "&screen_name="+screen_name
	else:
		return "Error"
	parameters = []
	try:
		response = twitterreq(url, "GET", parameters)
		result = response.read().decode("utf-8")
		jresult = json.loads(result)
	except:
		return list()
	try:
		if jresult["next_cursor"] !=0:
			id_post_writer.write(screen_name+"\n")
		friends = jresult["ids"]
		return friends
	except:
		return list()

# Output: 1. id_post_file: record now crawl users, 2. relationship_file
# Description: output the friends
def getUsersFriendship():
	usernames = ut.readLine2List(path, "usernames")
	counts = 0
	# from where to start
	with open(path + relationshipFileName, "r") as fi:
		count = len(fi.readlines())
	id_post_writer = open(path+"friends_over1page", "a")
	with open(path+relationshipFileName, "a", encoding="utf-8") as fo:
		for username in usernames[count:]:
			print(username)
			time.sleep(60)
			friends = getUserFriendship(id_post_writer, "", username, )
			friends = [str(a) for a in friends]
			fo.write(username+" "+",".join(friends)+"\n")
		
# Return: list of tweet 
# Description: get the tweets from the user with max = 5000 tweet +retweet
def getUserTweets(user_id="", screen_name=""):
	tweets = list()
	url = "https://api.twitter.com/1.1/statuses/user_timeline.json?trim_user=false&include_rts=1&"
	if user_id != "":
		url = url + "&user_id="+user_id
	elif screen_name != "":
		url = url + "&screen_name="+screen_name
	else:
		return "Error"
	parameters = []
	try:
		response = twitterreq(url, "GET", parameters)
		result = response.read().decode("utf-8")
		jresult = json.loads(result)
	except:
		return tweets()
	if type(jresult)==list:
		tweets = tweets + jresult
		maxId = str(int(jresult[-1]["id_str"])-1)
		while (len(jresult)>0 and len(tweets)<5000):
			time.sleep(5)
			urlNext = url+"&max_id="+maxId
			response = twitterreq(urlNext, "GET", parameters)
			result = response.read().decode("utf-8")
			jresult = json.loads(result)
			if len(jresult) > 0:
				tweets = tweets + jresult
				maxId = str(int(jresult[-1]["id_str"])-1)
	return tweets	

# Output: write tweet to username file in wall folder
def getUsersTweets():
	usernames = ut.readLine2List(path, "usernames")
	usernamesCrawled = ut.readLine2List(path, "id_post_file")
	fi = open(path+idPostFileName, 'a')
	for username in usernames[len(usernamesCrawled):]:
		print(username)
		time.sleep(5)
		tweets = getUserTweets("",username)
		# file cannot be opened due to wrong name
		try:
			with codecs.open(path+"wall/"+username, "w", encoding="utf-8") as fo:
				fo.write(json.dumps(tweets, indent=4, ensure_ascii=False))
		except:
			pass
		fi.write(username+'\n')







# Description: deprecated
def getUsersData():
	path = "../data/"
	sn = "twitter"
	snFolder = path+sn+"/"	
	# init file
	ut.initFolder(snFolder)

	tmpids = ut.readLine2List(snFolder, "tmpid_file")
	tmpids = [uid for uid in allids if uid not in ids]
	id_writer = open(snFolder+"id_file", 'a', encoding="utf8")
	allid_writer = open(snFolder+"allid_file", 'a', encoding="utf8")
	id_record_writer = open(snFolder+"id_record_file", 'a', encoding="utf8")

	profile_writer = open(snFolder+"profile_file", 'a', encoding="utf8")
	rela_writer = open(snFolder+"relationship_file", 'a', encoding="utf8")

	mapping = ut.readCommaLine2List(path, "twitterMapping")
	screenNames = [a[1].split("/")[-1].strip() for a in mapping]

	for screenName in screenNames:
		print(screenName)
		time.sleep(5)
		profile = getUserProfile(screen_name=screenName)
		try:
			uid = str(profile["id"])
		except:
			continue
		fids = getUserFriendship(user_id=uid)
		fids = [str(a) for a in fids]
		# tweets = getUserTweets(screen_name=screenName)
		# for fid in fids:
			# allid_writer.write(fid+"\n")
		# allid_writer.write(uid+"\n")
		# id_writer.write(uid+"\n")
		# profile_writer.write(json.dumps(profile)+'\n')
		rela_writer.write(uid+" "+",".join(fids)+'\n')
		# with open(snFolder+"wall/"+uid,"w") as fo:
		# 	fo.write(json.dumps(tweets))

	# except for the already parsed screenName
	# for screenName in screenNames:


def writeUserName():
	mapping = ut.readCommaLine2List("../data/", "twitterMapping")
	usernames = list()
	for m in mapping:
		url = m[1]
		username = url.split("/")[-1].strip()
		if username=="":
			username = url.split("/")[-2]
		if username=="#%21" or "twitter.com" in username:
			continue
		usernames.append(username)
	with open(path+"usernames", "w") as fo:
		for username in usernames:
			fo.write(username+"\n")

def pretify():
	with open(path+"wall/11586422", "r") as fi:
		jresult = json.loads(fi.read())
	with codecs.open(path+"wall/11586422", "w", encoding="utf-8") as fo:
		fo.write(json.dumps(jresult, indent=4, ensure_ascii=False))


if __name__ == '__main__':
	# writeUserName()
	# fetchsamples()
	# print(getUserFriendship(user_id="17004618"))

	getUsersFriendship()
	# getUsersTweets()
	# getUsersProfile()
