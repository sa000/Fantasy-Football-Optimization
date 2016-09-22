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




def grab_odds():
	browser = webdriver.Chrome()
	url='https://sports.bovada.lv/football/nfl/game-lines-market-group'
	browser.get(url)
	time.sleep(5)
	elem = browser.find_element_by_tag_name("body")
	print "Getting ready"
	no_of_pagedowns=7
	target=open('bovadaodds.csv', 'w')
	csvwriter=csv.writer(target)
	print 'initiial%s'%no_of_pagedowns
	while no_of_pagedowns>0:
		print 'in loop'
		elem.send_keys(Keys.PAGE_DOWN)
		time.sleep(0.5)
		no_of_pagedowns-=1
    	print 'loop%s'%no_of_pagedowns
	bet_games=[]
	game_id=1
	games=browser.find_elements_by_xpath('//*[@id="spaNavigationComponents_content_center"]/div/section/div/div/div/article')
	headers=["Game", 'Team', 'Team Opponent', 'Spread ', 'Volume']
	csvwriter.writerow(headers)
	print 'grabbing data'
	for game in games:
		team1=game.find_element_by_xpath('header/h3[1]').text.encode('utf-8')
		team2=game.find_element_by_xpath('header/h3[2]').text.encode('utf-8')

		spread1=game.find_element_by_xpath('section/ul[1]/li[1]/button/span[1]').text.encode('utf-8')
		spread1_para=game.find_element_by_xpath('section/ul[1]/li[1]/button/span[2]').text.encode('utf-8')
		spread1_final=spread1+spread1_para

		spread2=game.find_element_by_xpath('section/ul[1]/li[2]/button/span[1]').text.encode('utf-8')
		spread2_para=game.find_element_by_xpath('section/ul[1]/li[2]/button/span[2]').text.encode('utf-8')
		spread2_final=spread2+spread2_para

		total1=game.find_element_by_xpath('section/ul[3]/li[1]/button/span[1]').text.encode('ascii', 'ignore')
		total1_para=game.find_element_by_xpath('section/ul[3]/li[1]/button/span[2]').text.encode('ascii', 'ignore')
		total1_final=total1+total1_para

		total2=game.find_element_by_xpath('section/ul[3]/li[2]/button/span[1]').text.encode('ascii', 'ignore')
		total2_para=game.find_element_by_xpath('section/ul[3]/li[2]/button/span[2]').text.encode('ascii', 'ignore')
		total2_final=total2+total2_para

		team1_data=[game_id, team1, team2, spread1_final, total1_final]
		team2_data=[game_id, team2, team1, spread2_final, total2_final]
		print team1_data, team2_data
		csvwriter.writerow(team1_data)
		csvwriter.writerow(team2_data)

		game_id+=1
		time.sleep(1)
		print "game%d" % game_id

	target.close()

grab_odds()

	