import sys

import mechanize

uri = "https://plus.google.com/110356488025922357921/about"
uri = sys.argv[1]

request = mechanize.Request(uri)
response = mechanize.urlopen(request)
forms = mechanize.ParseResponse(response, backwards_compat=False)
response.close()
## f = open("example.html")
## forms = mechanize.ParseFile(f, "http://example.com/example.html",
##                              backwards_compat=False)
## f.close()
form = forms[0]
# print form  # very useful!
form["Email"] = "sychen1990@gmail.com"
form["Passwd"] = "PIpi09087358"
request2 = form.click()
try:
    response2 = mechanize.urlopen(request2)
except mechanize.HTTPError, response2:
	pass
# print response2.geturl()
print (response2.read())
# # headers
# for name, value in response2.info().items():
# 	if name != "date":
# 		print "%s: %s" % (name.title(), value)
# 		print response2.read()  # body
response2.close()