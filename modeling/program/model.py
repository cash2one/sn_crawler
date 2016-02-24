import utility as ut
import evaluate as el
outputPath = "../output/"
predictionPath = "../prediction/"
featureRankFilename = "features_rank"
featureNmFilename = "features_nm"
featureMnaFilename = "features_mna"

predictionNmFilename = "nm_1558.txt"
predictionMnaFilename = "mna_1558.txt"


'''
Name Matching
'''

def nm(threshold=0.67):
	instances = ut.readCommaLine2List(outputPath, featureNmFilename)
	predictions = list()
	count = 0
	for instance in instances:
		if (float(instance[1]) > threshold) or (float(instance[2])>threshold):
			count += 1
			predictions.append("1")
		else:
			predictions.append("0")
	ut.writeList2Line(predictionPath, predictionNmFilename, predictions)

def nmGrid():
	tBest = 0.6
	fBest = 0
	tStart = 0.67
	alpha = 0.01
	for i in range(10):
		t = tStart+alpha*i
		print(t)
		nm(t)
		f = el.evalNm()
		if fBest < f:
			fBest = f
			tBest = t
	nm(tBest)
	print("Best:"+str(t), str(f))


'''
MNA (Multiple Network Anchoring)
'''

# def mna():



def mnaConstraint():
	predictions = ut.readLine2List(outputPath, predictionMnaFilename)


if __name__ == "__main__":
	nm()
	# nmGrid()