import os
import pandas as pd

def condense_projections():
	files=os.listdir('Week1/merged')
	dataframes=[]
	print "building"
	headers=['Player', 'Position', 'Fantasy Points', 'FP Deviation']
	for file in files:
		print file
		df=pd.read_csv('Week1/merged/'+file)
		dataframes.append(df)
	merged = pd.concat(dataframes)
	columns=['player','position', 'Fantasy Points', 'FP deviation']
	for col in merged.columns:
		if 'Unnamed' in col:
			del merged[col]
	merged.to_csv('merged_projections_week1.csv', index=False, columns=columns)

def recalc_fpts():
	pd=read
if __name__ == '__main__':
	condense_projections()

