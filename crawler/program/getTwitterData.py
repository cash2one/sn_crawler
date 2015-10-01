import oauth2 as oauth
import urllib.request

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
	url = "https://api.twitter.com/1.1/friends/ids.json?cursor=-1&screen_name=sychen1990&count=5000"
	parameters = []
	response = twitterreq(url, "GET", parameters)
	for line in response:
		print (line.strip())


def getUserProfile():
	# write here 

def getUserSocialNetwork():

def getUserTweets():
	

if __name__ == '__main__':
	fetchsamples()
