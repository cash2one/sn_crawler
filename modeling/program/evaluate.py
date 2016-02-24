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
	preds = ut.readLine2List(predPath, filename)
	gts = ut.readLine2List(predPath, gtFilename)
	return evaluate(gts, preds)

def evalMna():
	print("Evaluation: Name")


def evalPvm():
	print("Evaluation: Profile Vector Matching")





if __name__ == "__main__":
	main()