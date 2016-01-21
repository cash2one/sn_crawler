
# Description: feature selection
def postprocess_feature(path="../output/", filename="features"):
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

if __name__=="__main__":
	postprocess_feature()