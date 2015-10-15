# -*- coding: utf-8 -*-
import networkx as nx
import urllib
import os
import math
import utility as ut
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import time
import multiprocessing as mp

# This file is for parsing relationship and profiles on google plus


# snList = ["facebook", "twitter", "linkedin", "pinterest", "plus.google", "tumblr", "instagram", "VK", "flickr", "Vine", "youtube", "github"]
snList = ["youtube", "facebook", "twitter", "linkedin", "flickr", "instagram", "tumblr", "github", "pinterest", "plus.google"]
path = "../data/"
root = "109675028280981323746"
snFolder = path+"google/"

# Description: parallel version to parse data
def getGoogleUsersParellel():
	ids = ut.readLine2List(snFolder, "id_file")
	allids = ut.readLine2List(snFolder, "allid_file")
	# nextids = allids[len(ids)+1:]
	nextids = list(set(allids)-set(ids))

	# write file
	id_error_writer = open(snFolder+"id_error_writer", "a")
	id_writer = open(snFolder+"id_file", 'a', encoding="utf8")
	allid_writer = open(snFolder+"allid_file", 'a', encoding="utf8")
	id_record_writer = open(snFolder+"id_record_file", 'a', encoding="utf8")

	sn_writer = open(snFolder+"sn_file", 'a', encoding="utf8")
	profile_writer = open(snFolder+"profile_file", 'a', encoding="utf8")
	rela_writer = open(snFolder+"relationship_file", 'a', encoding="utf8")

	# init the next users and record them in the graph
	if len(allids) == 0:
		allids.append(root)
	g = initGraph(allids, ids)
	index = 0

	# multiprocess to get the user info
	procNum = 6
	batchNum = 200
	drivers = list()
	lock = mp.Lock()
	for i in range(procNum):
		drivers.append(webdriver.Firefox())
	while index < len(nextids):
		result = list()
		q = mp.Queue()
		roundNum = procNum * batchNum
		procs = list()
		# count the process users
		if index+roundNum < len(nextids):
			for i in range(procNum):
				batchids = nextids[index+i*batchNum:index+((i+1)*batchNum)]
				p = mp.Process(target=worker, args=(batchids,q, drivers[i]))
				p.start()
				procs.append(p)
			for i in range(roundNum):
				result += q.get()
			for proc in procs:
				proc.join()
		else:
			batchids = nextids[index:]
			p = mp.Process(target=worker, args=(batchids,q, drivers[0]))
			p.start()
			result += q.get()
			p.join()
		# process back data 
		# lock.acquire()
		for userData in result:
			# dictionary: {id: uid, status: false or true,infos: infos, friends: friends, friend_bool: true, sns: sns, sn_bool: true false}
			uid = userData["id"]
			infos = userData["infos"]
			friends = userData["friends"]
			sns = userData["sns"]
			sn_bool = userData["sn_bool"]
			friend_bool = userData["friend_bool"]
			status = userData["status"]

			if g.node[uid]["status"] == 1:
				# print("already in graph")
				continue
			elif status==False:
				# print("cannot read be parsed")
				id_error_writer.write(uid+"\n")
			else:
				# print("new user")
				if infos != None:
					# writeUser2File(uid, sns, sn_bool, infos, friends, friend_bool, sn_writer, profile_writer, rela_writer, id_writer, id_record_writer)
					# print("start to write:"+uid)
					sn_writer.write(uid+','+','.join(sns)+'\n')
					profile_writer.write(uid+',\t'+',\t'.join(infos)+'\n')
					rela_writer.write(uid+' '+','.join(friends)+'\n')
					id_writer.write(uid+"\n")
					id_record_writer.write(uid)
					if sn_bool:
						id_record_writer.write(","+str(1))
					else:
						id_record_writer.write(","+str(0))
					if friend_bool:
						id_record_writer.write(","+str(1)+"\n")
					else:
						id_record_writer.write(","+str(0)+'\n')
					# print("finish write")
					addFriend(g, friends, allids, allid_writer, nextids)
					g.node[uid]["status"] = 1
					ids.append(uid)
				else:
					print("no info")
					id_writer.write(uid+"\n")
		# lock.release()
		index = index + procNum*batchNum
	for i in range(procNum):
		drivers[i].close()


# write the worker here
def worker(batchids, q, driver):
	# init driver
	# driver = webdriver.Firefox()
	for uid in batchids:
		error = 0
		print(uid)
		while True:
			try:
				if error == 5:
					q.put([{"id": uid, "status": False, "infos": None, "friends": None,"friend_bool": None, "sns": None, "sn_bool": None}])
					break
				else:
					output = parseGoogleUserParellel(driver, uid)
					q.put([output])
					break
			except:
				error = error+1
	# driver.close()


# Input: driver, user id
# Output: 
# Return: dictionary
def parseGoogleUserParellel(driver, uid):
	urlPrefix = "https://plus.google.com/"
	urlAbout = urlPrefix+uid+"/about"
	driver.get(urlAbout)
	html = driver.page_source
	soup = BeautifulSoup(html, "html5lib")
	sns, sn_bool = getGoogleUserSocialNetwork(soup)
	infos = getGoogleUserProfile(soup)
	if infos != None:
		friends, friend_bool = getGoogleUserRelationship(driver)
		return {"id": uid, "status": True, "infos": infos, "friends": friends, "friend_bool": friend_bool, "sns": sns, "sn_bool": sn_bool}
	else:
		return {"id": uid, "status": True, "infos": None, "friends": None, "friend_bool": None, "sns": None, "sn_bool": None}

# Description: single process version
def getGoogleUsers(sn = "google"):
	driver = getDriver()
	loginGoogle(driver)
	# init variable
	snFolder = path+sn+"/"
	ids = ut.readLine2List(snFolder, "id_file")
	allids = ut.readLine2List(snFolder, "allid_file")
	nextids = allids[len(ids)+1:]
	id_error_writer = open(snFolder+"id_error_writer", "a")


	if len(allids)==0:
		allids.append(root)
	# build social network here
	g = initGraph(allids, ids)

	for uid in nextids:
		# if uid not in ids:
		error = 0
		print(uid)
		# iterate until parse successfully
		while True:
			try:
				if error == 5:
					id_error_writer.write(str(uid)+"\n")
					break
				if parseGoogleUser(driver, g, snFolder, uid, ids, allids, nextids):
					break
			except:
				error = error+1
				pass
		# just add new ids here, don't delete the user id
	driver.close()


# def parseGoogleUser(driver, id, id_writer, allid_writer, rela_writer, sn_writer, profile_writer, content_path):
def parseGoogleUser(driver, g, snFolder, uid, ids, allids, nextids):
	s = time.time()
	urlPrefix = "https://plus.google.com/"
	urlAbout = urlPrefix+uid+"/about"
	# urlPosts = urlPrefix+uid+"/posts"
	# init file 
	ut.initFolder(snFolder)
	id_writer = open(snFolder+"id_file", 'a', encoding="utf8")
	allid_writer = open(snFolder+"allid_file", 'a', encoding="utf8")
	id_record_writer = open(snFolder+"id_record_file", 'a', encoding="utf8")

	sn_writer = open(snFolder+"sn_file", 'a', encoding="utf8")
	profile_writer = open(snFolder+"profile_file", 'a', encoding="utf8")
	rela_writer = open(snFolder+"relationship_file", 'a', encoding="utf8")
	# id
	driver.get(urlAbout)
	html = driver.page_source
	soup = BeautifulSoup(html, "html5lib")

	sns, sn_bool = getGoogleUserSocialNetwork(soup)
	infos = getGoogleUserProfile(soup)
	if infos != None:
		friends, friend_bool = getGoogleUserRelationship(driver)
		# posts
		# post_num = writeGoogleUserWall(driver, snFolder, urlPosts, uid)

		# add id
		# ids.append(uid)

		addFriend(g, friends, allids, allid_writer, nextids)
		g.node[uid]["status"] = 1
		writeUser2File(uid, sns, sn_bool, infos, friends, friend_bool, sn_writer, profile_writer, rela_writer, id_writer, id_record_writer)
		# write file

		# if post_num>0:
		# 	id_record_writer.write(","+str(1)+"\n")
		# else:
		# 	id_record_writer.write(","+str(0)+"\n")

		e = time.time()
		print(uid+" spend time:"+str(e-s))
	else:
		id_writer.write(uid+"\n")
	return True

def getGoogleUserSocialNetwork(soup):
	sns = [""]*len(snList)
	sn_bool = False
	try:
		linkModule = soup.find("div", {"class":"Ee g5a vna Yjb"})
		if linkModule!=None:
			linkRows = linkModule.findAll("a", {"class":"OLa url Xvc"})
			if len(linkRows) > 0:
				sn_bool = True
			for row in linkRows:
				link = row["href"]
				# which social network
				index = -1
				for i in range(len(snList)):
					sn = snList[i]
					if sn in link:
						index = i
						break
				if index != -1:
					sns[index] =  link
				else:
					# print(link)
					pass
		return sns, sn_bool
	except:
		print("sn error")
		return sns, sn_bool

# Input: soup of about html
# Output: list of information of profile
# titleStr = "uid,name,gender,birthday,other names,\
# 			school1,department1,school1_from,school1_to,desc1,school2,department2,school2_from,school2_to,desc2,school3,department3,school3_from,school3_to, desc3\
# 			occupation,skills,, corp1, job1, job1From, job1To, description1, corp2, job2, job2From, job2To, description2, corp3, job3, job3From, job3To, description3 \
# 			currentPlace,previousPlace1,previousPlace2"]
def getGoogleUserProfile(soup):
	basics = parseGoogleProfileBasic(soup)
	educations = parseGoogleProfileEducation(soup)
	works = parseGoogleProfileWork(soup)
	places = parseGoogleProfileLocation(soup)
	if basics == None:
		return None
	else:
		infos = basics+educations+works+places
		return infos

# Input: soup of about html
# Output: [name, gender, birthday, other names]
def parseGoogleProfileBasic(soup):
	basics = [""]*5
	name = soup.find("div", {"class":"rna KXa Xia fn"}).getText()
	basics[0] = name
	# infoTitles = ["性別","生日","感情狀態","其他名字"]
	infoTitles = ["Name","Gender", "Birthday", "Relationship", "Other names"]
	infoModule = soup.find("div", {"class":"Ee e5a vna Hqc"})
	try:
		infoRows = infoModule.findAll("div", {"class": "wna"})
		for row in infoRows:
			keyValue = row.findAll("div")
			key = keyValue[0].getText()
			value = keyValue[1].getText()
			try:
				basics[infoTitles.index(key)] = value
			except:
				continue
		return basics
	except:
		return None


# Input: soup of about html
# Output: [school1, department1, from1, to1, desc1] * 3
def parseGoogleProfileEducation(soup):
	educations = [""]*15
	eduModule = soup.find("div", {"class":"Ee h5a vna Jqc"})
	if eduModule!=None:
		eduRows = eduModule.findAll("li", {"class":"UZa"})
		# select top 3 educations
		if len(eduRows) > 3:
			eduRows = eduRows[:3]
		for i in range(len(eduRows)):
			row = eduRows[i]
			school = row.find("div", {"class":"PLa"}).getText().strip()
			eduInfo = row.findAll("div", {"class": "ija"})
			# have department, time, description
			if len(eduInfo) == 2:
				desc = eduInfo[1].getText().strip().replace("\n", " ")
			else:
				desc = ""
			department, eduFrom, eduTo = ut.parseTitleTime(eduInfo[0].getText())
			index = 5*i
			educations[index] = school
			educations[index+1] = department
			educations[index+2] = eduFrom
			educations[index+3] = eduTo
			educations[index+4] = desc
		for i in range(len(eduRows),3):
			for j in range(5):
				educations[i*5+j] = ""
	return educations


# Input: soup of about html
# Output: [occupation, skills, corp1, job1, job1From, job1To, description1, corp2, job2, job2From, job2To, description2, corp3, job3, job3From, job3To, description3]
# Descripiton: one skill, one occupation, many employments
def parseGoogleProfileWork(soup):
	works = [""]*17
	# workTitles = ["職業","技能","工作經歷"]
	workTitles = ["Occupation", "Skills", "Employment"]
	workModule = soup.find("div", {"class":"Ee l5a vna Tqc"})
	if workModule != None:
		occupation = ""
		skills = ""
		workRows = workModule.findAll("div", {"class":"wna"})
		for row in workRows:
			title = row.find("div", {"class":"Cr"}).getText()
			# Occupation
			if title == workTitles[0]:
				occupation = row.find("div", {"class":"y4"}).getText()
				works[0] = occupation
			# Skills 
			elif title==workTitles[1]:
				skills = row.find("div", {"class":"y4"}).getText()
				works[1] = skills
			# Employment
			else:
				employRows = row.findAll("li",{"class":"UZa"})
				if len(employRows)>3:
					employRows = employRows[:3]
				for i in range(len(employRows)):
					row = employRows[i]
					corp = row.find("div", {"class":"PLa"}).getText().strip()
					employInfo = row.findAll("div", {"class":"ija"})
					if len(employInfo) == 2:
						description = employInfo[1].getText().strip().replace("\n", " ").replace("\t", " ")
					else:
						description = ""
					job, jobFrom, jobTo = ut.parseTitleTime(employInfo[0].getText())
					index = i*5+2
					works[index] = corp
					works[index+1] = job
					works[index+2] = jobFrom
					works[index+3] = jobTo
					works[index+4] = description
				for i in range(len(employRows),3):
					for j in range(5):
						works[2+i*5+j] = ""
	return works

# Input: soup of about html
# Output: [current, previous1, previous2]
def parseGoogleProfileLocation(soup):
	places = [""]*3
	placeTitles = ["Currently", "Previously"]
	# placeTitles = ["目前", "先前"]
	placeModule = soup.find("div", {"class":"Ee i5a vna CVb"})
	if placeModule != None:
		placeRows = placeModule.findAll("div",{"class":"AAa"})
		for row in placeRows:
			time = row.find("div",{"class":"Cr"}).getText().strip()
			place = row.find("div",{"class":"y4"}).getText().strip().replace("\n"," ")
			if time == placeTitles[0]:
				places[0] = place.strip()
			else:
				previousPlaces = place.split("-")
				if len(previousPlaces) > 1:
					places[1] = previousPlaces[-1].strip().replace("\n", " ")
					places[2] = previousPlaces[-2].strip().replace("\n", " ")
				else:
					places[1] = place
					places[2] = "" 
	return places

# Input: web driver
# Output: friend id list
# rowHeight = 588 (relationship)

def getGoogleUserRelationship(driver):
	friends = list()
	friend_bool = False
	wait = WebDriverWait(driver, 10)
	try:
		wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR,"span.d-s.r5a")))
		span = driver.find_element_by_css_selector("span.d-s.r5a")
		friend_num = int(span.text.split(" ")[0])
		# chrome need it
		# time.sleep(friend_num*0.01)
		span.click()
		
		frame = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, ".wja.oha.b-K")))
		# time.sleep(0.5)
		# return how many time to scroll height
		friend_num = int(span.text.split(" ")[0])
		scrollTimes = math.floor(friend_num / 12)
		scrollLast = -(friend_num % 12)
		scrollTop = 0
		for i in range(scrollTimes):
			# print(i)
			scrollTop = i * 588
			driver.execute_script("var e=document.getElementsByClassName(\"wja oha b-K\")[0];e.scrollTop=%s;" % scrollTop)
			fids = [a.get_attribute("oid") for a in frame.find_elements(By.CSS_SELECTOR, ".ob.Jk")]
			# links = frame.find_elements(By.CSS_SELECTOR, ".ob.Jk")
			# for link in links:
			# 	fid = link.get_attribute("oid")
			# 	friends.append(fid)
			# if chrome need it
			# time.sleep(0.5)
			friends = friends+fids
		if scrollLast < 0:
			driver.execute_script("var e=document.getElementsByClassName(\"wja oha b-K\")[0];e.scrollTop=%s;" % scrollTop)
			fids = [a.get_attribute("oid") for a in frame.find_elements(By.CSS_SELECTOR, ".ob.Jk")[scrollLast:]]
			friends = friends+fids
		friend_loaded = len(friends)
		# print(friend_loaded)
		if len(friends) > 0:
			friend_bool = True
		return friends, friend_bool
	except:
		print("no friends")
		return friends, friend_bool

# Input: driver, url of post page, uid
# Output: wall content file named by uid
# Return: len of posts
def writeGoogleUserWall(driver,snFolder, urlPosts, uid):
	filePath = snFolder+"wall/"+uid
	posts = getGoogleUserPosts(driver, urlPosts)
	with open(filePath, 'w', encoding="utf8") as fo:
		for post in posts:
			fo.write(post+"\n")
	return len(posts)

# Input: driver, url of post page
# Output: posts
def getGoogleUserPosts(driver, urlPosts):
	posts = list()
	driver.get(urlPosts)
	wait = WebDriverWait(driver, 10)
	wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "div.pga")))
	count = 0
	more_load = driver.find_element_by_css_selector("div.R4.b2.Xha")
	while more_load.is_displayed() and count < 50:
		count += 1
		more = driver.find_element_by_css_selector("span.d-s.L5.r0").click()
		load = driver.find_element_by_css_selector("span.dP.PA")
		while(load.is_displayed()):
			continue
	html = driver.page_source
	soup = BeautifulSoup(html, "html5lib")
	postRows = soup.findAll("div", {"class":"Yp yt Xa"})
	for row in postRows:
		# time, text, video title
		try:
			time = row.find("a",{"class":"o-U-s FI Rg"}).get("title")
		except:
			time = " "
		try:
			text = row.find("div", {"class":"Ct"}).getText()[:-8]
		except:
			text = " "
		try:
			video = row.find("a", {"class":"kq ot-anchor"}).getText()
		except:
			video = " "
		try:
			post = time + "\t" + text + "\t" + video
			posts.append(post)
		except:
			posts.append("")
	print(len(posts))
	return posts


def getDriver():
	# firefox 
	# profile = webdriver.FirefoxProfile()
	# profile.set_preference("intl.accept_languages","en-us"); 
	# profile.set_preference("font.language.group","x-western")
	return	webdriver.Firefox()
	# login

	# chrome
	# options = webdriver.ChromeOptions()
	# options.add_argument('--lang=en')
	# driver = webdriver.Chrome(chrome_options=options)


def loginGoogle(driver):
	driver.get("https://plus.google.com/")
	email_input = driver.find_element_by_id("Email")
	email_input.send_keys("imsorry1121@gmail.com")
	next_btn = driver.find_element_by_id("next").click()
	WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.ID, "Passwd")))
	pwd_input = driver.find_element_by_id("Passwd")
	pwd_input.send_keys("PIpi09087358")
	login_btn = driver.find_element_by_id("signIn").click()

def initGraph(allids, ids):
	g = nx.Graph()
	for uid in allids:
		g.add_node(uid, status=0) 
	for uid in ids:
		g.node[uid]["status"] = 1
	return g

def addFriend(g, friends, allids, allids_writer, nextids):
	for friend in friends:
		try:
			g.node[friend]
		except:
			g.add_node(friend, status=0)
			allids.append(friend)
			allids_writer.write(friend+"\n")
			nextids.append(friend)

def writeUser2File(uid, sns, sn_bool, infos, friends, friend_bool, sn_writer, profile_writer, rela_writer, id_writer, id_record_writer):
	print("start to write:"+uid)
	sn_writer.write(uid+','+','.join(sns)+'\n')
	profile_writer.write(uid+',\t'+',\t'.join(infos)+'\n')
	rela_writer.write(uid+' '+','.join(friends)+'\n')
	id_writer.write(uid+"\n")
	id_record_writer.write(uid)
	if sn_bool:
		id_record_writer.write(","+str(1))
	else:
		id_record_writer.write(","+str(0))
	if friend_bool:
		id_record_writer.write(","+str(1)+"\n")
	else:
		id_record_writer.write(","+str(0)+'\n')
	print("finish write")


def reviseIdFile():
	ids = ut.readLine2List(snFolder, "id_file2")
	allids = ut.readLine2List(snFolder, "allid_file")
	loss = ut.readLine2List(snFolder, "tmp_ids")

	# revise id file duplicate problem
	g=nx.Graph()
	dup = list()
	num = list()
	for i in range(len(allids)):
		id = allids[i]
		try:
			g.node[id]
			dup.append(id)
			num.append(i)
		except:
			g.add_node(id)
	print(len(dup))
	for i in range(len(num)-1, -1, -1):
		pos = num[i]
		del allids[pos]
	for l in loss:
		allids.append(l)
	ut.writeList2Line("../data/google/", "allid_file2", allids)
	
	# loss = list(set(allids[:(len(ids))])-set(ids))
	# ut.writeList2Line("../data/google/", "tmp_ids", loss)




if __name__ == "__main__":
	# getGoogleUsers()
	getGoogleUsersParellel()

	# reviseIdFile()
	# html = ""
	# with open("html", "r") as fi:
	# 	html = fi.read()
	# soup = BeautifulSoup(html, "html5lib")
	# getGoogleUserSocialNetwork(soup)
