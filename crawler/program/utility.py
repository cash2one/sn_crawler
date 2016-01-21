import os
import shutil
# File Related

def initFolder(snFolder):
	if not os.path.isdir(snFolder):
		os.mkdir(snFolder)
	if not os.path.isdir(snFolder+"wall"):
		os.mkdir(snFolder+"wall")

# Input: file location
# Output: list
def readLine2List(path, fileName):
	result = list()
	try:
		with open(getFileLocation(path, fileName), "r") as fi:
			for line in fi:
				result.append(line.strip())
		return result
	except:
		return result


def readCommaLine2List(path, fileName):
	results = list()
	try:
		with open(getFileLocation(path, fileName), "r") as fi:
			for line in fi:
				results.append(line.strip().split(","))
		return results
	except:
		return results

def writeList2Line(path, fileName, results):
	if results != None and len(results)>0:
		with open(getFileLocation(path, fileName), "w") as fo:
			for result in results:
				fo.write(result+'\n')

def writeList2CommaLine(path, fileName, results):
	if results != None and len(results)>0:
		with open(getFileLocation(path, fileName), "w") as fo:
			for result in results:
				outputStr = ",".join(result)+'\n'  
				fo.write(outputStr)

def getFileLocation(path, fileName):
	fileLocation = ""
	if path[-1]=="/":
		fileLocation = path+fileName
	else:
		fileLocation = path+"/"+fileName
	return fileLocation

# Input: " 2014 - 2015 " or null string
# Output: from, to
def parseTime(time):
	try:
		period = time.strip().split("-")
		timeFrom = period[0].strip()
		timeTo = period[1].strip()
		return timeFrom, timeTo
	except:
		return "", ""

# Input: title time string
# Output: title, from, to
def parseTitleTime(string):
	string = string.strip()
	if string != "":
		titleTime = string.split(",")		
		if len(titleTime) == 1:
			if "-" in string:
				try: 
					title = ""
					timeFrom, timeTo = parseTime(string)
					int(timeFrom)
				except:
					title = string
					timeFrom, timeTo = "", ""
			else:
				title = string
				timeFrom, timeTo = "", ""
		else:
			title = titleTime[0]
			time = titleTime[1]
			timeFrom, timeTo = parseTime(time)
		return title, timeFrom, timeTo
	else:
		return "", "", ""

# Description: browser will store the browsing history in the disk
# /c/Users/ken/AppData/Local/Temp/tmpXXXX
def removeWinSpace():
	path = "C:/Users/ken/AppData/Local/Temp/"
	folders = list()
	for dirname in os.listdir(path):
		if dirname[:3] == "tmp":
			print(dirname)
			try:
				shutil.rmtree(path+dirname)
			except:
				pass
	# 

if __name__=="__main__":
	removeWinSpace()