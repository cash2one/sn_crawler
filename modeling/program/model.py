import utility as ut
import evaluate as el
from sklearn import svm
import operator
import sys

sys.setrecursionlimit(10000)
outputPath = "../output/"
predPath = "../prediction/"
featureRankFilename = "features_rank"
featureNmFilename = "features_nm"
featureMnaFilename = "features_mna"

predictionRankConstraintFilename = "ranking_constraint_1558.txt"
predictionRankFilename = "ranking_1558.txt"
predictionRankOriginFilename = "ranking_origin_1558.txt"
predictionNmFilename = "nm_1558.txt"
predictionMnaFilename = "mna_1558.txt"
predictionMnaOriginFilename = "mna_origin_1558.txt"


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


def rankingConstraint(n=1558):
	scores = ut.readLine2List(predPath, predictionRankOriginFilename)
	users1 = list()
	users2 = dict()
	predictions = list()
	results = list()
	# init
	for i in range(n):
		users2[i] = {"active": 0, "user": 0, "index": 0, "score": 0}
	for i in range(n):
		scores_i = scores[n*i:n*(i+1)]
		users1.append(sorted(enumerate(scores_i), key=lambda k: k[1]))
	# choose one mapping 
	for i in range(n):
		findMapping(users1, users2, i, 0)
	results = sorted([(v["user"], k) for k, v in users2.items()], key=operator.itemgetter(0))
	for pair in results:
		user2 = pair[1]
		predictions_i = ["0"]*n
		predictions_i[user2] = "1"
		predictions+=predictions_i
	ut.writeList2Line(predPath, predictionRankConstraintFilename, predictions)	

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



def mnaConstraint(n=1558):
	scores = ut.readLine2List(predPath, predictionMnaOriginFilename)
	users1 = list()
	users2 = dict()
	predictions = list()
	results = list()
	# init
	for i in range(n):
		users2[i] = {"active": 0, "user": 0, "index": 0, "score": 0}
	for i in range(n):
		scores_i = scores[n*i:n*(i+1)]
		users1.append(sorted(enumerate(scores_i), key=lambda k: k[1]))
	# choose one mapping 
	for i in range(n):
		findMapping(users1, users2, i, 0)
	results = sorted([(v["user"], k) for k, v in users2.items()], key=operator.itemgetter(0))
	for pair in results:
		user2 = pair[1]
		predictions_i = ["0"]*n
		predictions_i[user2] = "1"
		predictions+=predictions_i
	ut.writeList2Line(predPath, predictionMnaFilename, predictions)	





def findMapping(users1, users2, user1, index):
	# print(user1, index)
	scores_i = users1[user1]
	target = -1
	while(target==-1):
		target = scores_i[index][0]
		score = scores_i[index][1]
		if users2[target]["active"]==0:
			users2[target]["active"] = 1
			users2[target]["score"] = score
			users2[target]["index"] = index
			users2[target]["user"] = user1
		else:
			if (score > users2[target]["score"]):
				user1_next = users2[target]["user"]
				index_next = users2[target]["index"]
				users2[target]["score"] = score
				users2[target]["index"] = index
				users2[target]["user"] = user1
				print(user1_next, index_next)
				findMapping(users1, users2, user1_next, index_next+1)
			else:
				index += 1
				target = -1




if __name__ == "__main__":
	# ranking()
	rankingConstraint()
	# nm()
	# nmGrid()