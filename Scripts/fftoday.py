import requests
from lxml import html 
import numpy as np
import urllib
from bs4 import BeautifulSoup
import csv
import os
import pandas as pd
import shutil

def generate_urls(week):
	week=str(week)
	positions=['QB', 'RB', 'WR', 'TE', 'DEF']
	pos_urls=['10','20', '30', '40', '99']
	years=['2016']
	for index, pos_url in enumerate(pos_urls):
		for year in years:
			pos=positions[index]
			url='http://fftoday.com/stats/playerstats.php?Season='+year+'&GameWeek='+week+'&PosID='+pos_url+'&LeagueID=1&order_by=FFPts&sort_order=DESC&cur_page='
			print url
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
	else:
		for page in xrange(pages+1):
			urls.append(url+str(page))
	#print(urls)
	with open(filename, 'wb') as csvfile:
		csvwriter=csv.writer(csvfile)
		#get rid of the last 2 ff pt totals
		for url in urls:
			#print(url)
			print("getting data")
			page=requests.get(url)
			data=html.fromstring(page.content)
			headers=data.xpath('/html/body/center/table[2]/tr[2]/td[1]/table[6]/tr/td/table/tr[2]/td')
			headers=headers[0:len(headers)]
			col_names=[header.xpath('b/text()')[0] for header in headers]
			tablehdr=data.xpath('/html/body/center/table[2]/tr[2]/td[1]/table[6]/tr/td/table/tr[1]/td')
			tablehdr=tablehdr[0:len(tablehdr)]
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
				stats=player.xpath('td/text()')[1:]
				row=name+stats
				csvwriter.writerow(row)
	shutil.move(filename, '../Actual/%s' %filename)		

def clean_headers():
	files=os.listdir('../Actual/')
	print files

	for index, file in enumerate(files):
		if '.DS' in file:
			continue
		new_cols=[]

		df=pd.read_csv('../Actual/%s' %file)
		first_row=df.columns
		sec_row=df.iloc[0]
		# for index, entry in enumerate(first_row):
		# 	if 'Unnamed' in entry:
		# 		new_cols.append(' ')
		# 	else:
		# 		new_cols.append(entry)	
		# print new_cols, sec_row
		new_cols=new_cols+sec_row
		df.columns=new_cols
		df.to_csv(file)
		os.rename(file, '../Actual/%s' %file)

def merge_actual(week):
	path='../Actual/'
	files=os.listdir(path)
	dataframes=[]
	print files

	for index, file in enumerate(files):
		if '.DS' in file:
			continue
		df=pd.read_csv('../Actual/%s'%file)
		dataframes.append(df)
		print len(dataframes)
		print file
	merged=pd.concat(dataframes)

	
	merged.to_csv('merged_actual_week%d.csv'%week)
	# for col in merged.columns:
	# 	if 'Unnamed' in col:
	# 		del merged[col]


def clean_merged_actual(week):
	df=pd.read_csv('merged_actual_week%d.csv'%week)
	for index, row in df.iterrows():
		if row[1]=='FPts' and index>2:
			df.drop(index, inplace=True) 
			print "deleting"
	df.to_csv('merged_actual_%d.csv'%week)
	#os.rename('merged_actual_%d.csv'%week)

def recalculate():
	files=os.listdir('../Actual/')
	for file in files:
		print file
		if '.DS_' in file:
			continue
		df=pd.read_csv('../Actual/'+file,skiprows=[1])
		if 'DEF' in file:
			total_pts=df['Unnamed: 11']
			del df['Unnamed: 11']
			del df['Unnamed: 12']
		elif 'QB' in file:
			ffpoints=4*df['Passing.3']+.04*df['Passing.2']-df['Passing.4']+.1*df['Rushing.1']+6*df['Rushing.2']
			passing_bonus=np.where(df['Passing.2']>=300, 3,0)
			total_pts=ffpoints+passing_bonus
			print 'c1'
		elif 'RB' in file:
			rushing_bonus=np.where(df['Rushing.1']>=100,3,0)
			receiving_bonus=np.where(df['Receiving.2']>=100,3,0)
			total_pts=.1*df['Rushing.1']+6*df['Rushing.2']+df['Receiving.1']+.1*df['Receiving']+rushing_bonus+receiving_bonus
			print 'c2'
		elif 'WR' in file:
			print 'wr'
			rushing_bonus=np.where(df['Rushing.2']>=100,3,0)
			receiving_bonus=np.where(df['Receiving.2']>=100,3,0)
			total_pts=.1*df['Rushing.2']+6*df['Receiving.3']+df['Receiving.1']+.1*df['Receiving']+rushing_bonus+receiving_bonus
			print 'c3'
		else:
			receiving_bonus=np.where(df['Receiving.2']>=100,3,0)
 			total_pts=df['Receiving.1']+.1*df['Receiving.2']+6*df['Receiving.3']+receiving_bonus
		df['Fantasy']=total_pts
		if 'DEF' not in file:
			print file
			del df['Fantasy.1']
		df.to_csv(file)
		print 'Done'
		os.rename(file, '../Actual/%s' %file)

def accumulate_csv():
	files=os.listdir('../Actual')
	merged_csvs=[]
	week=1
	print files
	for file in files:
		if '.csv' not in file:
			continue
		print file
		df=pd.read_csv('../Actual/'+file)
		df['Week']=week
		merged_csvs.append(df)
		week+=1
	print len(merged_csvs)
	merged=pd.concat(merged_csvs)
	merged.to_csv('Accumulated_actual_data.csv')
def poop():
	print 'hey'
if __name__ == '__main__':
	week=3

	generate_urls(week)
	# #recalculate()
	# # #clean_headers()
	# #merge_actual(week)
	# #clean_merged_actual(week)
	# accumulate_csv()


