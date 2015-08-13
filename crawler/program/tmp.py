import mechanize as mc
import cookielib
from bs4 import BeautifulSoup
import urllib
from selenium import webdriver

snList = ["facebook", "twitter", "linkedin", "pinterest", "plus.google", "tumblr", "instagram", "VK", "flickr", "Vine", "youtube", "github"]
def crawlGooglePlus(uid):
	# set the crawler to english
	urlPrefix = "https://plus.google.com/"
	urlSuffix = "/about"
	url = urlPrefix+uid+urlSuffix

	webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.customHeaders.Accept-Language'] = 'zh-tw,en-US'
	browser = webdriver.PhantomJS()
	browser.get(url)
	try:
		# people in my circle
		browser.find_element_by_class_name("d-s.r5a").click()
	except:
		print("no circle in the google plus")
	# html = browser.find_element_by_tag_name("body").get_attribute("innerHTML")
	html = browser.page_source
	print(html)
	soup = BeautifulSoup(html)
	# print(soup)
	# basic information: gender, birthday, relationship, other name
	infoModule = soup.find("div", {"class":"Ee e5a vna Hqc"})
	infoRows = infoModule.findAll("div", {"class": "wna"})
	infoDict = dict()
	for row in infoRows:
		keyValue = row.findAll("div")
		key = keyValue[0].getText()
		value = keyValue[1].getText()
		infoDict[key] = value
	print("info")
	print(infoDict)
	# education: school, from, to
	eduList = list()
	eduModule = soup.find("div", {"class":"Ee h5a vna Jqc"})
	if eduModule!=None:
		eduRows = eduModule.findAll("li", {"class":"UZa"})
		for row in eduRows:
			school = row.find("div", {"class":"PLa"}).getText()
			try: 
				tmpValues = row.find("div", {"class":"ija"}).getText().split(',')
				department = tmpValues[0]
			except:
				department = None
			try:
				period = tmpValues[1].split('-')
				timeStart = period[0].strip()
				timeEnd = period[1].strip()
			except:
				# eduList.append({"school":school, "department": department})
				timeStart = None
				timeEnd = None
			eduList.append({"school":school, "department":department, "timeStart":timeStart, "timeEnd":timeEnd})
	print('education')
	print(eduList)

	# social friend and follower
	careDict = dict()
	followDict = dict()
	careModule = soup.find("div", {"class":"Tnb y6a oz-sg-elements"})
	if careModule != None:
		friends = careModule.findAll("a", {"class":"n0b"})
		print(len(friends))
		for friend in friends:
			name = frined.getText()
			fid = friend.get("oid")
			careDict[fid] = name
	print("people in my circle")
	print(careDict)

	try:
		html2 = browser.find_element_by_class_name("d-s.o5a").click()
		soup2 = BeautifulSoup(html2)
		followModule = soup2.find("div", {"class":"Tnb y6a oz-sg-elements"})
		if followModule != None:
			followers = followModule.findAll("a", {"class":"n0b"})
			for follower in followers:
				name = frined.getText()
				fid = friend.get("oid")
				followDict[fid] = name
	except:
		print("i am in no people circle")
	print(followDict)

	# work: employment(skill, occupation, firm) 
	workDict = dict()
	workModule = soup.find("div", {"class":"Ee l5a vna Tqc"})
	if workModule != None:
		workRows = workModule.findAll("div", {"class":"wna"})
		for row in workRows[:-1]:
			key = row.find("div", {"class":"Cr"}).getText()
			value = row.find("div", {"class":"y4"}).getText()
			workDict[key] = value
		employList = list()
		employ = workRows[-1]
		for employment in employ.findAll("div", {"class":"PLa"}):
			employList.append(employment.getText())
	print("work")
	print(workDict)

	# place: location
	placeDict = dict()
	placeModule = soup.find("div", {"class":"Ee i5a vna CVb"})
	if placeModule != None:
		placeRows = placeModule.findAll("div",{"class":"AAa"})
		for row in placeRows:
			time = row.find("div",{"class":"Cr"}).getText()
			place = row.find("div",{"class":"y4"}).getText()
			placeDict[key] = time
	print("place")
	print(placeDict)

	# links: other social network link
	linkModule = soup.find("div", {"class":"wna fa-TCa Ala"})
	linkDict = dict()
	if linkModule!=None:
		linkRows = linkModule.findAll("li")
		for row in linkRows:
			link = row.find("a").get("href")
			snTarget = link
			for sn in snList:
				if sn in link:
					snTarget = sn
					break
			linkDict[snTarget]=link
	print("link")
	print(linkDict)
	browser.close()


def crawlTwitter(uid):
	print("crawl twitter")


if __name__ == "__main__":
	# google plus id list
	ids = ["106309407311701947463", "111867549117983525241", "109675028280981323746", "110356488025922357921", ]
	crawlGooglePlus("111867549117983525241")
