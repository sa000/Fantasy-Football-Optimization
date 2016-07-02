import requests
from lxml import html 
import numpy as np
import urllib
from bs4 import BeautifulSoup
import csv
import os


def generate_urls():
	weeks=[str(i+1) for i in xrange(17)]
	positions=['QB', 'RB', 'WR', 'TE']
	pos_urls=['10','20', '30', '40']
	year='2015'
	for week in weeks:
		for index, pos_url in enumerate(pos_urls):
			pos=positions[index]
			url='http://fftoday.com/stats/playerstats.php?Season='+year+'&GameWeek='+week+'&PosID='+pos_url+'&LeagueID=1&order_by=FFPts&sort_order=DESC&cur_page='
			grab_data(url, year, week, pos)

def grab_data(url, year, week, pos):
	filename=pos+'Week'+week+year+'.csv'
	print(filename)
	#Find number of pages
	find_next=True
	pages=0
	while find_next:
		htmltext=urllib.urlopen(url+str(pages))
		#print(url+str(pages))
		soup = BeautifulSoup(htmltext, 'html.parser')
		next_page = soup.findAll(text="Next Page")
		if next_page !=[]:
			pages=pages+1
		else:
			find_next=False
	urls=[]
	print(pages)
	if pages==0:
		urls=[url+str(pages)]
	for page in xrange(pages+1):
		urls.append(url+str(page))
	print(urls)
	with open(filename, 'wb') as csvfile:
		csvwriter=csv.writer(csvfile)
		#get rid of the last 2 ff pt totals
		for url in urls:
			print(url)
			print("getting data")
			page=requests.get(url)
			data=html.fromstring(page.content)
			headers=data.xpath('/html/body/center/table[2]/tr[2]/td[1]/table[6]/tr/td/table/tr[2]/td')
			headers=headers[0:len(headers)-2]
			col_names=[header.xpath('b/text()')[0] for header in headers]
			tablehdr=data.xpath('/html/body/center/table[2]/tr[2]/td[1]/table[6]/tr/td/table/tr[1]/td')
			tablehdr=tablehdr[0:len(tablehdr)-1]
			col_header=[]
			for index, title in enumerate(tablehdr):
				title_hdr=[]
				length=int(title.xpath('@colspan')[0])
				if index==0 or pos in ['K', 'DEF', 'DL', 'LB', 'DB']:
					spaces=['' for x in xrange(length)]
					col_header=col_header+spaces
				else:
					title_name=title.xpath('text()')[0]
					title_hdr=[title_name for x in xrange(length)]
				col_header=col_header+title_hdr
			if url[-1]=='0':
				csvwriter.writerow(col_header)
				csvwriter.writerow(col_names)
			players=data.xpath('/html/body/center/table[2]/tr[2]/td[1]/table[6]/tr/td/table/tr')
			players=players[2:len(players)]
			row=[]
			for player in players:
				name=player.xpath('td[1]/a/text()')
				stats=player.xpath('td/text()')[1:-2]
				row=name+stats
				csvwriter.writerow(row)

if __name__ == '__main__':
	generate_urls()



