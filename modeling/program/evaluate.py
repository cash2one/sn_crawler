import utility as ut
import numpy as np
import operator

evalPath = "../evaluation/"
predPath = "../prediction/"
gtFilename = "gt"


def main():
	# evalRanking()
	evalNm()

# Input: prediction list and ground truth list (two-class)
# precision and recall
def evaluate(gts, preds):
	tp, tn, fp, fn = 0, 0, 0, 0
	for i, gt in enumerate(gts):
		p = preds[i]
		if gt == "1":
			if p == "1":
				tp += 1
			else:
				fn += 1
		else:
			if p == "1":
				fp += 1
			else:
				tn += 1
	print("TP:"+str(tp), "TN:"+str(tn), "FP:"+str(fp), "FN:"+str(fn))
	precision = (tp)/(tp+fp)
	recall = tp/(tp+fn)
	accu = (tp+tn)/(len(gts))
	f = 2 * precision * recall/(precision+recall)
	print("Precision:" + str(precision))
	print("Recall:"+ str(recall))
	print("Accuracy:"+ str(accu))
	print("F-measure:"+ str(f))
	return f

def evalNm(filename="nm_1558.txt"):
	print("Evaluation: Name Matching")
	preds = ut.readLine2List(predPath, filename)
	gts = ut.readLine2List(predPath, gtFilename)
	return evaluate(gts, preds)


def evalRanking(filename="ranking_1558.txt"):
	print("Evaluation: Ranking")
	gts, preds = prepRanking(1558, )
	evaluate(gts, preds)

def evalMna():
	print("Evaluation: Name")


def evalPvm():
	print("Evaluation: Profile Vector Matching")


# merge ranking and scores files
def prepRanking(n=1558, filename="ranking_1558.txt"):
	scores = ut.readLine2List(predPath, filename)
	preds = list()
	gts = ut.readLine2List(predPath, gtFilename)
	for i in range(n):
		# print(i*n)
		scores_i = scores[i*n:(i+1)*n]
		max_index = max(enumerate(scores_i), key=lambda k: float(k[1]))[0]
		# print(max_index)
		preds_i = ["0"]*1558
		preds_i[max_index] = "1"
		preds += preds_i
	return gts, preds


if __name__ == "__main__":
	main()