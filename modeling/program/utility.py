# coding=utf8
import os
import shutil
import json
import time
import math
# language
import pyxdameraulevenshtein
import langid
import langdetect
from textblob import TextBlob
import nltk
from nltk.corpus import stopwords
import jieba
# from jNlp.jTokenize import jTokenize
import tinysegmenter
import string
from stemming.porter2 import stem
import textrazor


'''
File
'''
def initFolder(snFolder):
	if not os.path.isdir(snFolder):
		os.mkdir(snFolder)
	if not os.path.isdir(snFolder+"wall"):
		os.mkdir(snFolder+"wall")

def readRankFeature(path, filename):
	instances = list()
	with open(getFileLocation(path, filename), "r") as fi:
		for line in fi:
			instance = dict()
			data = line.strip().split(" ")
			instance["gt"] = data[0]
			instance["qid"] = data[1].split(":")
			for feature in data[2:-2]:
				tmp = feature.split(":")
				instance[tmp[0]] = tmp[1]
			instances.append(instance)
	print(len(instances))
	return instances



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

def readJson2Dict(path, fileName):
	try:
		with open(getFileLocation(path, fileName), "r", encoding="utf8") as fi:
			return json.loads(fi.read())
	except:
		return dict()

def writeDict2Json(path, fileName, result):
	try:
		with open(getFileLocation(path, fileName), "w", encoding="utf8") as fo:
			fo.write(json.dumps(result, indent=4, ensure_ascii=False))
	except:
		print("write file error")

def writeList2Json(path, fileName, result):
	try:
		with open(getFileLocation(path, fileName), "w", encoding="utf8") as fo:
			fo.write(json.dumps(result, indent=4, ensure_ascii=False))
	except:
		print("write file error")	

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


'''Data Structure'''
def getDistri(elements):
	distri = dict()
	for e in elements:
		distri[e] = distri.get(e, 0)+1
	return distri

def mergeDict(dl):
	result = dict()
	for d in dl:
		for key, value in d.items():
			result[key] = result.get(key, 0) + value
	return result

def addDict(d1, d2):
	for key, value in d1.items():
		d2[key] = d2.get(key, 0) + value
	return d2

def normVectorDict(d):
	for key, vector in d.items():
		d[key] = normVector(vector)
	return d

def normVector(vector):
	denominator = math.sqrt(sum([math.pow(value,2) for value in vector.values()]))
	for key in vector.keys():
		vector[key] /= denominator
	return vector

# Description: average the list of values in value of dictionary
def avgDict(d):
	result = dict()
	if len(d)>0:
		for key, values in d.items:
			result[key] = sum(values)/len(values)
	return result


'''Time'''

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

def parseSNTime(string):
	t = time.strptime(string, "%Y-%m-%dT%H:%M:%S")
	return t


'''Place'''


'''Language'''
def detectLang(string):
	lang = ""
	if string != "":
		try:
			if len(string)>=3:
				lang = TextBlob(string).detect_language()[:2]
			else:
				lang = langid.classify(string)[0]
		except:
			pass
	return lang

def wordProcess(sentence, lang):
	# no use stopword, tf-idf will ignore those stopwords
	rule = string.punctuation+" "
	if lang=="zh":
		tokens = jieba.lcut(sentence, cut_all=False)
		tokens = [t.strip() for t in tokens if t.strip()!="" and t.strip() not in rule]
	elif lang == "jp":
		jtk = tinysegmenter.TinySegmenter()
		tokens = jtk.tokenize(sentence)
		tokens = [t.strip() for t in tokens if t.strip()!="" and t.strip() not in rule]
	else:
		tokens = nltk.word_tokenize(sentence.lower())
		if lang=="en":
			tokens = [stem(t.strip()) for t in tokens if t.strip()!="" and t.strip() not in rule]
		else:
			tokens = [t.strip() for t in tokens if t.strip()!="" and t.strip() not in rule]
	return getDistri(tokens)



# Input: text and language
# Return: translate the text to english
def translate(string, lang):
	return ""
	tb = TextBlob(string)
	if lang != "en":
		try:
			tb = tb.translate(to="en")
		except:
			pass
	return str(tb)

# Return: sentiment
# Input: english sentence
def getSentiment(string):
	return {"polarity":0, "subjectivity":0}
	tb = TextBlob(string)
	sentiment = {"polarity":tb.sentiment.polarity, "subjectivity":tb.sentiment.subjectivity}
	return sentiment

# def getSentiment2(string, lang):


def getTopic(string):
	return dict()
	topic_distri = dict()
	if string=="":
		return topic_distri
	textrazor.api_key = "528d21faef2b391e46cc77bfa8b1a9d28dd00a7f77ee562f2811520a"
	client = textrazor.TextRazor(extractors=["topics"])
	response = client.analyze(string)
	for topic in response.coarse_topics():
		topic_distri[topic.label] = topic.score
	return topic_distri


def stringDistance(string1, string2):
	return pyxdameraulevenshtein.normalized_damerau_levenshtein_distance(string1, string2)



'''Others'''
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


if __name__=="__main__":
	# removeWinSpace()
	# getTopic("Her Code Got Humans on the Moon—And Invented Software Itself http://t.co/NAHqCNoaJT via @WIRED")
	getTopic("Her code was awesome，but 不知道別人的")