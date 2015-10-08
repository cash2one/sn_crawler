import oauth2 as oauth
import urllib.request
import json
import utility as ut
import time

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
idRecordFileName = "id_record_file"
profileFileName = "profile_file"
relationshipFileName = "relationship_file"
# Construct, sign, and open a twitter request
# using the hard-coded credentials above.
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
	response = twitterreq(url, "GET", parameters)
	result = response.read().decode("utf-8")
	jresult = json.loads(result)
	return jresult

def getUserFriendship(user_id="", screen_name=""):
	url = "https://api.twitter.com/1.1/friends/ids.json?cursor=-1&count=5000"
	if user_id != "":
		url = url + "&user_id="+user_id
	elif screen_name != "":
		url = url + "&screen_name="+screen_name
	else:
		return "Error"
	parameters = []
	response = twitterreq(url, "GET", parameters)
	result = response.read().decode("utf-8")
	print(result)
	jresult = json.loads(result)
	try:
		friends = jresult["ids"]
		return friends
	except:
		return list()
		

def getUserTweets(user_id="", screen_name=""):
	url = "https://api.twitter.com/1.1/statuses/user_timeline.json?trim_user=false"
	if user_id != "":
		url = url + "&user_id="+user_id
	elif screen_name != "":
		url = url + "&screen_name="+screen_name
	else:
		return "Error"
	parameters = []
	response = twitterreq(url, "GET", parameters)
	result = response.read().decode("utf-8")
	jresult = json.loads(result)
	return jresult	


# def getUserData():



def getUsersData():
	path = "../data/"
	sn = "twitter"
	snFolder = path+sn+"/"	
	# init file
	ut.initFolder(snFolder)
	ids = ut.readLine2List(snFolder, "id_file")
	allids = ut.readLine2List(snFolder, "allid_file")
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




if __name__ == '__main__':
	# fetchsamples()
	# print(getUserFriendship(user_id="17004618"))

	# getUserProfile()
	# getUserTweets()
	getUsersData()
