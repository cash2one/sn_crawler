import urllib.request
import json
import utility as ut
import codecs
import time
# get google plus data by google plus api
# just post and profile, cannot get relationship


apiPrefix = "https://www.googleapis.com/plus/v1/people/"
key = "?key=AIzaSyDQjrGhUlsgX6wxryil8elEPJtJKdSUW8U"
apiPostPostfix = "/activities/public"

path = "../data/google/"
statPath = "../data/stat/"
idProfileFileName = "id_profile_file"
idPostFileName = "id_post_file"
idsMapping = "ids_mapping"

def getUsers():
	# url ="https://www.googleapis.com/plus/v1/people/105774718778616150593/people/visible?orderBy=best&key=AIzaSyDQjrGhUlsgX6wxryil8elEPJtJKdSUW8U"
	api = apiPrefix+"105774718778616150593" +key
	# +apiPostfix
	json = urllib.request.urlopen(url).read()
	# get next page token by 
	print(json)

# Description: Get google plus users profile
def getUsersProfile():
	print("get users profile")
	userids = ut.readLine2List(path, "ids_mapping")
	useridsCrawled = ut.readLine2List(path, idProfileFileName)
	useridsLeft = list(set(userids)-set(useridsCrawled))
	fi = open(path+idProfileFileName, 'a')
	for userid in useridsLeft:
	# for userid in userids[len(useridsCrawled):]:
		time.sleep(8)
		print(userid)
		profile = getUserProfile(userid)
		with codecs.open(path+"profile/"+userid, "w", encoding="utf-8") as fo:
			fo.write(json.dumps(profile, indent=4, ensure_ascii=False))
		fi.write(userid+'\n')

def getUserProfile(userid):
	try:
		url = apiPrefix+userid+key
		result = urllib.request.urlopen(url).read()
		profile = json.loads(result.decode("utf-8"))
		return profile
	except:
		return {"status":"error"}

# Description: Get google plus users post
def getUsersPost():
	print("get users post")
	userids = ut.readLine2List(path, "ids_mapping")
	useridsCrawled = ut.readLine2List(path, idPostFileName)
	useridsError = ut.readLine2List(statPath, "google_ids_post_errors")
	useridsLeft = list(set(userids)-set(useridsCrawled))
	# fi = open(path+idPostFileName, 'a')
	# fi.write("start")
	# for userid in useridsError:
	for userid in useridsLeft:
		# timer here
		# fi.write(userid+'\n')
		with open(path+idPostFileName, "a") as fi:
			fi.write(userid+"\n")
		print(userid)
		posts = getUserPost(userid)
		time.sleep(8)
		with codecs.open(path+"wall/"+userid, "w", encoding="utf-8") as fo:
			fo.write(json.dumps(posts, indent=4, ensure_ascii=False))

def getUserPost(userid):
	try:
		posts = list()
		url = apiPrefix+userid+apiPostPostfix+key
		result = urllib.request.urlopen(url).read()
		jresult = json.loads(result.decode("utf-8"))
		posts.append(jresult)
	except:
		print(userid)
		return {"status":"error"}
	try:
		# one result 20 posts
		while jresult["nextPageToken"] and len(posts)<=50:
			time.sleep(8)
			pageToken = jresult["nextPageToken"]
			urlNext = url+"&pageToken="+pageToken
			result = urllib.request.urlopen(urlNext).read()
			jresult = json.loads(result.decode("utf-8"))
			posts.append(jresult)
	except:
		return posts





def test():
	with open(path+idPostFileName, "a") as fi:
		fi.write("test")

if __name__ == "__main__":
	# getUsers()
	# getUserPost("100013290597972346821")
	getUsersPost()
	# getUserProfile("103169532913084862537")
	# getUsersProfile()
	# writeUserIds()
