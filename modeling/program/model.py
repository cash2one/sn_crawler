import utility as ut
import evaluate as el
import operator
import sys
import sklearn
import sklearn.cross_validation as cv
import feature2 as ft
import numpy as np
import random
from sklearn import svm

sys.setrecursionlimit(10000)
outputPath = "../output/"
predPath = "../prediction/"
featureRankFilename = "features_rank"
featureNmFilename = "features_nm"
featureMnaFilename = "features_mna"
featureSvmFilename = "features_svm"
featureLinkFilename = "features_link"

predictionRankConstraintFilename = "ranking_constraint_1558.txt"
predictionRankFilename = "ranking_1558.txt"
predictionRankOriginFilename = "ranking_origin_1558.txt"
predictionNmFilename = "nm_1558.txt"
predictionMnaFilename = "mna_1558.txt"
predictionMnaOriginFilename = "mna_origin_1558.txt"
predictionMnaConstraintFilename = "mna_constraint_1558.txt"


'''
CLF (collective link fusion)
'''


def clf(n=1558, filename="clf_1558.txt"):
	# read link and features
	# 1.build formation probability (for social and anchor)
	# 	a. data split for 5 folds
	# 	b. pu learning to build model_f by model and transition probability
	# 	c. get formation probability 
	data_anchor = np.loadtxt(outputPath+featureSvmFilename, delimiter=",")
	data_social = np.loadtxt(outputPath+featureLinkFilename, delimiter=",0")
	# build anchor formation probability and its model
	data = data_anchor
	data = np.append(data, np.zeros((len(data),1)), 1)
	data = sampleData(data)
	# 這邊data要加入那個node到哪個node不然無法產生matrix
	
	# X = data[:,0]
	# Y = data[0]
	kf = cv.KFold(n=len(data), n_folds=5, shuffle=True)
	for train_index, test_index in kf:
		getFormProb(train_index, test_index, data)
	print(data[:,-1])
	# get node name and its formation prob
	# 這邊只有少量的data有些link沒有放進來，傳入data 
	matrix = getMatrix(links)
	# 2. Use formation probability to random walk, alpha s=0.6, alpha a=0.6, c = 0.1
	# ps, pt, ws, wt, wts, wst

	


def getMatrix():
	gids, tids = getGt()
	nodes = gids+tids
	matrix = np.empty([len(nodes),len(nodes)])

	links_g = getSocialLinks("../intermediate/google/relationship", gids)
	links_t = getSocialLinks("../intermediate/twitter/relationship", tids)
	links = links_g+links_t
	for link in links:
		uid1, uid2 = link
		index1 = nodes.index(uid1)
		index2 = nodes.index(uid2)
		matrix[index1,index2]=1
		matrix[index2,index1]=1




	# read two graph node and its social links
	# read two

# Description: pu learning + feature extraction
# def getSocialLinkFeatures():
# 

# Description: get fully aligment ids
# Return: two social networks ids
def getGt(filename="../intermediate/gt"):
	gids = list()
	tids = list()
	with open(filename, "r") as fi:
		for line in fi:
			gid, tid  = line.split(",")
			gids.append(gid)
			tids.append(tid)
	return sorted(gids), sorted(tids)

# Description: get social links among specific ids
# Return: id pair between them
def getSocialLinks(filename="../intermediate/google/relationship", uids):
	links = list()
	with open(filename, "r") as fi:
		for line in fi:
			sid, tid_str = line.strip().split(" ")
			if sid not in uids:
				continue
			tids = tid_str.split(",")
			for tid in tids:
				if tid in uids:
					links.append((sid, tid))
	return links

def getFormProb(train_index, test_index, data):
	valid_index = train_index[len(train_index)-len(test_index):]
	train_index = train_index[:len(train_index)-len(test_index)]
	data_train, data_valid, data_test = data[train_index], data[valid_index], data[test_index]
	model = trainModel(data_train)
	t_p = getTransProb(model, data_valid)
	p_form_test = getTestFormProb(t_p, data_test[:,1:-1], model)
	for index, t_index in enumerate(test_index):
		data[t_index,-1] = p_form_test[index]


def getTestFormProb(t_p, x, model):
	p_test = model.predict_proba(x)[:,1]
	p_form_test = [p/t_p for p in p_test]
	return p_form_test

def getTransProb(model, data):
	pos_index = np.where(data[:,0]==1)
	p = model.predict_proba(data[:,1:-1])[:,1]
	t_p = sum(p)/len(pos_index)
	return t_p

def trainModel(data):
	model = svm.SVC(probability=True)
	model.fit(data[:,1:-1], data[:,0])

'''
Random Walk
'''

def randomWalk(matrix, p, c):
	p_next = list(p)
	for i in range(1000):
		p_next = (1-c)*np.dot(matrix, p_next)+c*p
	return p_next
'''
PU Learning
'''
# Description: get the positive and real negative set, can be applied to anchor link or social link
# Return: model f
# model, t, rn
def puLearn(data, alpha):
	# model1 for spy
	pos_index = np.where(data[:,0]==1)
	s_index = random.sample(pos_index, int(len(pos_index)*alpha))
	neg_index = np.where(data[:,0]==0)
	rn_index = list()
	data[s_index,0] = 0
	model_s = svm.SVC(probability=True)
	model_s.fit(data[:,1:], data[:,0])
	# predict the probability of s set

	probs_s = [model_s.predict_proba(s[:,1:])[0,1] for s in data[s_index]]
	t = min(probs_s)
	probs_neg = [model_s.predict_proba(neg[:,1:])[0,1] for neg in data[neg_index]]
	for index, prob in enumerate(probs_neg):
		if prob < t:
			rn_index.append(neg_index[index])
	data_f = np.concatenate((data[pos_index], data[rn_index]), axis=0)
	model_f = svm.SVC(probability=True)
	model_f.fit(data_f[:,1:], data_f[:,0])
	return model_f


'''
Others
'''
def sampleData(data):
	neg_index = np.where(data[:,0]==0)
	pos_index = np.ones(len(data), np.bool)
	pos_index[neg_index] = 0
	pos_data = data[pos_index]
	neg_samples = random.sample(neg_data, len(data)-len(neg_inst))
	data = np.concatenate((pos_data, neg_data), axis=0)
	return data

def sampleSpy(data):


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
	scores = [float(i) for i in ut.readLine2List(predPath, predictionRankOriginFilename)]
	oneMapping(scores, predictionRankConstraintFilename, n)

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
# result from libsvm



def mnaConstraint(n=1558):
	scores = list()
	with open(ut.getFileLocation(predPath, predictionMnaOriginFilename), "r") as fi:
		fi.readline()
		for line in fi:
			scores.append(float(line.strip().split()[1]))
	oneMapping(scores, predictionMnaConstraintFilename, n)


'''
Helper function
'''

# Input: Score file
# Output: Prediction
def oneMapping(scores, outputFilename=predictionRankConstraintFilename, n=1558):
	users1 = list()
	users2 = dict()
	predictions = list()
	results = list()
	# init
	for i in range(n):
		users2[i] = {"active": 0, "user": 0, "index": 0, "score": 0}
	for i in range(n):
		scores_i = scores[n*i:n*(i+1)]
		scores_i_sorted = sorted(enumerate(scores_i), key=lambda k: k[1], reverse=True)
		users1.append(scores_i_sorted)
	# choose one mapping 
	for i in range(n):
		oneMappingRecur(users1, users2, i, 0)
	results = sorted([(v["user"], k) for k, v in users2.items()], key=operator.itemgetter(0))
	for pair in results:
		user2 = pair[1]
		predictions_i = ["0"]*n
		predictions_i[user2] = "1"
		predictions+=predictions_i
	ut.writeList2Line(predPath, outputFilename, predictions)	




def oneMappingRecur(users1, users2, user1, index):
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
				# print(user1_next, index_next, score, users2[target]["score"])
				users2[target]["score"] = score
				users2[target]["index"] = index
				users2[target]["user"] = user1
				
				oneMappingRecur(users1, users2, user1_next, index_next+1)
			else:
				index += 1
				target = -1
	# result = sorted([(v["user"], k, v["score"]) for k,v in users2.items()], key=lambda k: k[0])
	# print(result)



if __name__ == "__main__":
	# ranking()
	# rankingConstraint()
	mnaConstraint()
	# nm()
	# nmGrid()