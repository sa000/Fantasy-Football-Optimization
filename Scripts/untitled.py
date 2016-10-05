import requests
from lxml import html 
import numpy as np
import urllib
from bs4 import BeautifulSoup
import csv
import os
import pandas as pd
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys


def grab_payoffs():
	browser = webdriver.Chrome()
	url='https://www.draftkings.com/mycontests'
	browser.get(url)
	time.sleep(7)
	print 'logging in'
	browser.find_element_by_xpath('//*[@id="login-link"]/span[1]').click()
	email='alamsakib@gmail.com'
	pw='alamed93'
	time.sleep(3)
	print' checking'
	username=browser.find_element_by_id('Username')
	password=browser.find_element_by_id('Password')
	username.send_keys(email)
	password.send_keys(pw)
	print ' logged in'
	# elem = browser.find_element_by_tag_name("body")
	# radio_elem= browser.find_element_by_xpath('/html/body/div[2]/div[2]/div[2]/div[2]/div[1]/div/label[3]/span')
	print "Getting ready"

grab_payoffs()