import utility as ut
import json
import feature as ft


inputPath = "../data/"
interPath = "../intermediate/"
outputPath = '../output/'

mappingFileName = "twitterMapping"
mappingLossFileName = "gt_loss"
gtLooseFileName = "gt_loose"
gtStrictFileName = "gt_strict"
sn1 = "google"
sn2 = "twitter"
twitterNameIdFileName = "twitterNameId"
twitterIdNameFileName = "twitterIdName"


def statNameScore():
	gtsLoose = ut.readCommaLine2List(interPath, gtLooseFileName)
	gtsStrict = ut.readCommaLine2List(interPath, gtStrictFileName)
	gts = gtsStrict
	twitterIdName = ut.readJson2Dict(interPath, twitterIdNameFileName)
	twitterNameId = ut.readJson2Dict(interPath, twitterNameIdFileName)
	results = list()

	for gt in gts:
		googleId = gt[0]
		twitterId = gt[1]
		twitterName = twitterIdName[twitterId]
		print(googleId)
		print(twitterName)
		googleProfile = ut.readJson2Dict(interPath+"google/profile/", googleId)
		twitterProfile = ut.readJson2Dict(interPath+"twitter/profile/", twitterName)
		nameScore = ft.calNameScore(googleProfile, twitterProfile)
		displaynameScore = ft.calDisplayNameScore(googleProfile, twitterProfile)
		totalScore = nameScore + displaynameScore
		results.append([googleId, twitterId, str(nameScore), str(displaynameScore), str(totalScore)])
	ut.writeList2CommaLine(interPath, "name_score", results)



if __name__ == "__main__":
	statNameScore()
