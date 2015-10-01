import utility as ut
import os
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import time
# open driver
pathData = "../data/twitter/"
allidFileName = "allid_file"
idFileName = "id_file"
idRecordFileName = "id_record_file"
snFileName = "sn_file"
profileFileName = "profile_file"
relationshipFileName = "relationship_file"

def getTwitterUsers():
	initFolder(pathData)
	# read the users from the file
	ut.readLine2List()


# login twitter website

# get data
# parse 

# write data



if __name__ == "__main__":
	print("parse twitter")