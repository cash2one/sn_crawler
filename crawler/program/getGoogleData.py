import urllib
import json
# get google plus data by google plus api
# just post and profile, cannot get relationship
api_key = ""
apiPrefix = "https://www.googleapis.com/plus/v1/people/"
key = "?key=AIzaSyDQjrGhUlsgX6wxryil8elEPJtJKdSUW8U"
apiPostfix = "/activities/public"
def getUsers():
	# url ="https://www.googleapis.com/plus/v1/people/105774718778616150593/people/visible?orderBy=best&key=AIzaSyDQjrGhUlsgX6wxryil8elEPJtJKdSUW8U"
	api = apiPrefix+"105774718778616150593" +key
	# +apiPostfix
	json = urllib.urlopen(url).read()
	# get next page token by 
	print(json)


if __name__ == "__main__":
	print("get google plus data by api")
	getUsers()
