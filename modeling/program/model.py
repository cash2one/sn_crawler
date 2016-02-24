import utility as ut
import evaluate as el
outputPath = "../output/"
predPath = "../prediction/"
featureRankFilename = "features_rank"
featureNmFilename = "features_nm"
featureMnaFilename = "features_mna"

predictionRankFilename = "ranking_1558.txt"
predictionNmFilename = "nm_1558.txt"
predictionMnaFilename = "mna_1558.txt"


'''
Ranking
'''
# merge ranking and scores files
def ranking(n=1558, filename="ranking_origin_1558.txt"):
	scores = ut.readLine2List(predPath, filename)
	preds = list()
	for i in range(n):
		# print(i*n)
		scores_i = scores[i*n:(i+1)*n]
		max_index = max(enumerate(scores_i), key=lambda k: float(k[1]))[0]
		# print(max_index)
		preds_i = ["0"]*1558
		preds_i[max_index] = "1"
		preds += preds_i
	ut.writeList2Line(predPath, predictionRankFilename, preds)
	return preds


# def rankingConstraint():

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
	ut.writeList2Line(predPath, predictionNmFilename, predictions)

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
	ranking()
	# nm()
	# nmGrid()