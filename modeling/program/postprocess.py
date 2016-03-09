import utility as ut

outputPath = "../output/"
predictionPath = "../prediction/"
featureRankFilename = "features_rank"
featureNmFilename = "features_nm"
featureMnaFilename = "features_mna"
featureSvmFilename = "features_svm"
gtFilename = "gt"

# Description: feature selection
def getRankingFeature(path="../output/", filename=featureRankFilename):
	fprofile = open(path+"profile_features", "w")
	fsocial = open(path+"social_features", "w")
	fbehavior = open(path+"behavior_features", "w")
	fbaseline = open(path+"baseline_features", "w")
	with open(path+filename, "r") as fi:
		for line in fi:
			data = line.strip().split(" ")
			gt = data[0]
			qid = data[1]
			profile = data[2:6]
			social = data[7:26]
			behavior = data[26:]
			baseline = data[:-10]
			fprofile.write(" ".join([gt,qid]+profile)+"\n")
			fsocial.write(" ".join([gt,qid]+social)+"\n")
			fbehavior.write(" ".join([gt,qid]+behavior)+"\n")
			fbaseline.write(" ".join(baseline)+"\n")


def getNmFeature():
	with open(ut.getFileLocation(outputPath, featureNmFilename), "w") as fo:
		with open(ut.getFileLocation(outputPath, featureRankFilename), "r") as fi:
			for line in fi:
				data = line.strip().split(" ")
				gt = data[0]
				features = [f.split(":")[1] for f in data[2:4]]
				fo.write(",".join([gt]+features)+"\n")

	# instances = ut.readRankFeature(outputPath, featureRankFilename)
	# rows = list()
	# for instance in instances:
	# 	rows.append([instance["gt"], str(instance["1"]), str(instance["2"])])
	# ut.writeList2CommaLine(outputPath, featureNmFilename, rows)

# def getPvmFeature():


def getMnaFeature():
	with open(ut.getFileLocation(outputPath, featureMnaFilename), "w") as fo:
		with open(ut.getFileLocation(outputPath, featureRankFilename), "r") as fi:
			for line in fi:
				data = line.strip().split(" ")
				gt = data[0]
				features = data[2:-2]
				fo.write(" ".join([gt]+features)+"\n")

def getSvmFeature():
	with open(ut.getFileLocation(outputPath, featureSvmFilename), "w") as fo:
		with open(ut.getFileLocation(outputPath, featureRankFilename), "r") as fi:
			for line in fi:
				data = line.strip().split(" ")
				gt = data[0]
				gid = data[1].split(":")[1]
				tid = data[-1]
				features = [f.split(":")[1] for f in data[2:-2]]
				if len(features)<50:
					features+=["0"]*(50-len(features))
				fo.write(",".join([gt,gid,tid]+features)+"\n")


def getGt(n=1558):
	gts = list()
	for i in range(n):
		for j in range(n):
			if i == j:
				gts.append("1")
			else:
				gts.append("0")
	ut.writeList2Line(predictionPath, gtFilename, gts)


if __name__=="__main__":
	# getNmFeature()
	# getMnaFeature()
	# getGt()
	getSvmFeature()
