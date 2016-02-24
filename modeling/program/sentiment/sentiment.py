import nltk
import jieba
from nltk.corpus import reuters

parsed_file = "data/data.txt"

def preprocess():
	data = list()
	origin = list()
	with open(parsed_file, "w") as fo:
		with open("corpus", 'r') as fi:
			for i in range(3000):
				label = fi.readline().strip()
				sentence = fi.readline().strip().split("|")[1]
				tokens = jieba.cut(sentence)
				fo.write(label+" "+" ".join(tokens)+'\n')
				# data.append({"label": label, "sentence": sentence})



if __name__ == "__main__":
	preprocess()
