import urllib.request
import json
import utility as ut
import codecs
# get google plus data by google plus api
# just post and profile, cannot get relationship
api_key = ""
apiPrefix = "https://www.googleapis.com/plus/v1/people/"
key = "?key=AIzaSyDQjrGhUlsgX6wxryil8elEPJtJKdSUW8U"
apiPostPostfix = "/activities/public"

path = "../data/google/"
idProfileFileName = "id_profile_file"
idPostFileName = "id_post_file"

def getUsers():
	# url ="https://www.googleapis.com/plus/v1/people/105774718778616150593/people/visible?orderBy=best&key=AIzaSyDQjrGhUlsgX6wxryil8elEPJtJKdSUW8U"
	api = apiPrefix+"105774718778616150593" +key
	# +apiPostfix
	json = urllib.request.urlopen(url).read()
	# get next page token by 
	print(json)

def getUserProfile(userid):
	try:
		url = apiPrefix+userid+key
		result = urllib.request.urlopen(url).read()
		profile = json.loads(result.decode("utf-8"))
		return profile
	except:
		return {"status":"error"}


def getUsersProfile():
	print("get users profile")
	userids = ut.readLine2List(path, "userids")
	useridsCrawled = ut.readLine2List(path, idProfileFileName)
	fi = open(path+idProfileFileName, 'a')
	for userid in userids[len(useridsCrawled):]:
		print(userid)
		profile = getUserProfile(userid)
		with codecs.open(path+"profile/"+userid, "w", encoding="utf-8") as fo:
			fo.write(json.dumps(profile, indent=4, ensure_ascii=False))
		fi.write(userid+'\n')


def getUserPost(userid):
	try:
		posts = list()
		url = apiPrefix+userid+apiPostPostfix+key
		result = urllib.request.urlopen(url).read()
		jresult = json.loads(result.decode("utf-8"))
		posts.append(jresult)
	except:
		return {"status":"error"}
	try:
		while jresult["nextPageToken"]:
			pageToken = jresult["nextPageToken"]
			urlNext = url+"&pageToken="+pageToken
			result = urllib.request.urlopen(urlNext).read()
			jresult = json.loads(result.decode("utf-8"))
			posts.append(jresult)
	except:
		# print(len(posts))
		return posts


def getUsersPost():
	print("get users post")
	userids = ut.readLine2List(path, "userids")
	useridsCrawled = ut.readLine2List(path, idPostFileName)
	# fi = open(path+idPostFileName, 'a')
	# fi.write("start")
	for userid in userids[len(useridsCrawled):]:
		# fi.write(userid+'\n')
		with open(path+idPostFileName, "a") as fi:
			fi.write(userid+"\n")
		print(userid)
		posts = getUserPost(userid)
		with codecs.open(path+"wall/"+userid, "w", encoding="utf-8") as fo:
			fo.write(json.dumps(posts, indent=4, ensure_ascii=False))


def writeUserIds():
	userids = list()
	with open("../data/twitterMapping", "r") as fi:
		for line in fi:
			uid = line.split(",")[0]
			userids.append(uid)
	# print(userids)
	ut.writeList2Line(path, "userids", userids)


def test():
	with open(path+idPostFileName, "a") as fi:
		fi.write("test")

if __name__ == "__main__":
	# getUsers()
	# getUserPost("110318982509514011806")
	getUsersPost()
	# getUserProfile("103169532913084862537")
	# getUsersProfile()
	# writeUserIds()
