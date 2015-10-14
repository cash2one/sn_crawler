from selenium import webdriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import multiprocessing as mp
from time import time
import utility as ut

# multiprocess for crawler is faster

def main():
	urls = list()
	ids = ut.readLine2List("../data/google/", "id_file")
	for i in range(10):
		uid = ids[i]
		urlPrefix = "https://plus.google.com/"
		urlAbout = urlPrefix+uid+"/about"
		urls.append(urlAbout)
	s = time()
	nprocs = 4
	procList = list()
	result = list()
	q = mp.Queue()
	index = 0 
	# driver = webdriver.Firefox()
	while index < len(urls):
		# url = urls[index]
		# index = index+1
		# driver.get(url)
		# result.append(driver.title)

		for i in range(nprocs):
			print(index)
			scope = 2
			urls_short = urls[index:index+scope]
			p = mp.Process(target=f, args=([3], q, urls_short))
			p.start()
			procList.append(p)
			index = index + scope
		print(q.qsize)
		for i in range(q.qsize()):
			result += q.get()
		for p in procList:
			p.join()
	e = time()
	print (result)
	print (e-s)


def f(num, q, urls):
	driver = webdriver.Firefox()
	for url in urls:
		driver.get(url)
	# html = driver.page_source
	# print(html)
	# text = html.find("a", {"class":"question-hyperlink"}).getText()
		title = driver.title
		q.put(title)
	driver.close()


if __name__ == '__main__':
	main()