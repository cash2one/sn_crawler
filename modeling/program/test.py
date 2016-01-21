import nltk
import time

sentence = "<b>Mike Elgan Radio 11: Echo</b><br /><br />Mike Elgan Radio is back!<br /><br />Listen here: <a href=\"http://mike-elgan-radio.madewithopinion.com/mike-elgan-radio-echo/#\">http://mike-elgan-radio.madewithopinion.com/mike-elgan-radio-echo/#</a><br /><br />Subscribe on iTunes: <br /><a href=\"https://itunes.apple.com/us/podcast/mike-elgan-radio/id1037649051?mt=2\">https://itunes.apple.com/us/podcast/mike-elgan-radio/id1037649051?mt=2</a><br /><br /> <a rel=\"nofollow\" class=\"ot-hashtag\" href=\"https://plus.google.com/s/%23MikeElganRadio\">#MikeElganRadio</a>"

s = time.time()
# for i in range(20):
	# sentence+=sentence
nltk.word_tokenize(sentence)
e = time.time()
print(e-s)