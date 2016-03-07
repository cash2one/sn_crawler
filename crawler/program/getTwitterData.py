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
idsSawFileName = "ids_saw"
idsVisitedFileName = "ids_visited"
idsRecordedFileName = "ids_recorded"

namesMappingFileName = "names_mapping"

idPostFileName = "id_post_file"
idProfileFileName = "id_profile_file"
profileFileName = "profile_file"
relationshipFileName = "relationship_file"

'''
Main
'''
# Construct, sign, and open a twitter request
# using the hard-coded credentials above.
# friends: 1/min, profile: 12/min, post: 12/min


'''
Profile
'''
# Description: get user profile and save it in profile
def getUsersProfile():
	# total user - crawled users before
	usernames = ut.readLine2List(path, namesMappingFileName)
	usernamesCrawled = ut.readLine2List(path, idProfileFileName)
	usernamesLeft = list(set(usernames)-set(usernamesCrawled))
	fi = open(path+idProfileFileName, 'a')
	for username in usernamesLeft:
	# for username in usernames[len(usernamesCrawled):]:
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

'''
Relationship
'''

# Output: 1. id_post_file: record now crawl users, 2. relationship_file
# Description: output the friends
def getUsersFriendship():
	usernames = ut.readLine2List(path, namesMappingFileName)
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
'''
Posts
'''

# Output: write tweet to username file in wall folder
def getUsersTweets():
	usernames = ut.readLine2List(path, namesMappingFileName)
	usernamesCrawled = ut.readLine2List(path, "id_post_file")
	usernamesLeft = list(set(usernames)-set(usernamesCrawled))
	fi = open(path+idPostFileName, 'a')
	for username in usernamesLeft:
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
	if type(jresult)==list and len(jresult)>0:
		tweets = tweets + jresult
		maxId = str(int(jresult[-1]["id_str"])-1)
		while (type(jresult) == list and len(jresult)>0 and len(tweets)<1000):
			time.sleep(5)
			urlNext = url+"&max_id="+maxId
			response = twitterreq(urlNext, "GET", parameters)
			result = response.read().decode("utf-8")
			jresult = json.loads(result)
			if len(jresult) > 0 and type(jresult)==list:
				tweets = tweets + jresult
				maxId = str(int(jresult[-1]["id_str"])-1)
	else:
		print(jresult)
	return tweets	

'''
API
'''
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


'''
Others
'''
# Description: twitter api using example
def fetchsamples():
	# url = "https://stream.twitter.com/1/statuses/sample.json"
	url = "https://api.twitter.com/1.1/friends/ids.json?cursor=-1&user_id=3140536897&count=5000"
	parameters = []
	response = twitterreq(url, "GET", parameters)
	for line in response:
		print (line.strip())

def pretify():
	with open(path+"wall/11586422", "r") as fi:
		jresult = json.loads(fi.read())
	with codecs.open(path+"wall/11586422", "w", encoding="utf-8") as fo:
		fo.write(json.dumps(jresult, indent=4, ensure_ascii=False))




if __name__ == '__main__':
	# fetchsamples()
	# print(getUserFriendship(user_id="17004618"))

	# getUsersFriendship()
	getUsersTweets()
	# getUsersProfile()
