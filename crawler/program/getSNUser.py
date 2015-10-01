import utility as ut
import parseGoogle as pg
import parseTwitter as pt
import os
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import time
# open driver
path = "../data/"
allidFileName = "allid_file"
idFileName = "id_file"
idRecordFileName = "id_record_file"
snFileName = "sn_file"
profileFileName = "profile_file"
relationshipFileName = "relationship_file"

def getSNUsers(sn):
	driver = webdriver.Firefox()

	if sn=="google":
		pg.loginGoogle(driver)
	elif sn == "twitter":
		pt.loginTwitter(driver)
	elif sn == "facebook":
		loginFacebook(driver)

	# init variable
	snFolder = path+sn+'/'
	ids = ut.readLine2List(snFolder, idFileName)
	allids = ut.readLine2List(snFolder, allidFileName)
	tmpids = [uid for uid in allids if uid not in ids]

	# init parse list
	if len(tmpids) == 0:
		if sn == "google":
			user = "109675028280981323746"
		elif sn == "twitter":
			user = "sychen1990"
		elif sn == "facebook":
			user = "100000338035879"
		tmpids.append(user)
		allids.append(user)
	for uid in tmpids:
		if uid not in ids:
			# time.sleep(2)
			print(uid)
			if sn == "google":
				pg.parseGoogleUser(driver, snFolder, uid, ids, allids, tmpids)
			elif sn == "twitter":
				pt.parseTwitterUser(driver, snFolder, uid, ids, allids, tmpids)
	driver.close()
	



if __name__ == "__main__":
	print("parse social network")
	getSNUsers("google")
