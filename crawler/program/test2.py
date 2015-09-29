# coding=utf-8
from bs4 import BeautifulSoup
import urllib2
import mechanize
import gzip
from selenium import webdriver
import selenium.webdriver.support.ui as ui

def loginGoogle():
	# fail: browser no longer support
	br = mechanize.Browser()
	br.set_handle_robots(True)
	br.set_debug_http(True)
	# br.set_debug_responses(True)
	# br.set_debug_redirects(True)

	# Add User-Agent
	# br.addheaders.append( ['Accept-Encoding','gzip'] )
	br.addheaders = [("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36")]
	br.addheaders = [("Accept-Language", "en")]

	# Browse to login page
	br.open('https://plus.google.com/')
	br.select_form(nr=0)

	# # Fill in username and password, submit
	br["Email"] = "sychen1990"
	response = br.submit()
	# print(response.read())
	# for form in br.forms():
		# print(form)
	form = br.select_form(nr=0)
	br["Passwd"] = "PIpi09087358"
	response2 = br.submit()
	print(response2.read())

def loginYahoo():
	# fail: parse error, need to compile in wide python to solve coding problem
	br = mechanize.Browser()
	br.set_handle_robots(True)
	br.set_debug_http(True)
	# br.set_debug_responses(True)
	# br.set_debug_redirects(True)

	# Add User-Agent
	# br.addheaders.append( ['Accept-Encoding','gzip'] )
	br.addheaders = [("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36")]
	br.addheaders = [("Accept-Language", "en")]

	# Browse to login page
	# br.open('https://plus.google.com/')
	br.open('https://login.yahoo.com/config/login')
	br.select_form(nr=0)
	br["username"] = "ironchen@yahoo-inc.com"
	br["passwd"] = "OUou0908&#%*"
	response = br.submit()
	print(response.read())


def clickGooglePlus():
	url = 'https://plus.google.com/106309407311701947463/about'
	browser = webdriver.PhantomJS()
	# browser = webdriver.Chrome('chromedriver.')
	browser.get(url)
	print("get finish")
	e = browser.find_element_by_class_name("d-s.r5a")
	print(e.get_attribute("innerHTML"))
	e.click()
	wait = ui.WebDriverWait(browser, 20)
	results = wait.until(lambda browser: browser.find_elements_by_class_name('Enb hSb Tcb'))
	print(results[0].text)
	# return none
	# print(browser.response())
	html = browser.page_source
	with open("click.txt", "w") as fo:
		fo.write(html.encode("utf-8"))
	# print(html)
	browser.close()

def loginTwitter():
	url = "https://twitter.com/"
	

if __name__ == "__main__":
	# loginGoogle()
	# loginYahoo()
	clickGooglePlus()

