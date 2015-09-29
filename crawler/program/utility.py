# Input: file location
# Output: list
def readFileByLine(path):
	result = list()
	try:
		with open(path, "r") as fi:
			for line in fi:
				result.append(line.strip())
		return result
	except:
		return result

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
				title = ""
				timeFrom, timeTo = parseTime(string)
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

