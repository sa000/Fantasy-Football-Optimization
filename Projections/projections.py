import pandas as pd
import os
import numpy as np
from scipy import stats as scistats
import pdb;
def add_salary():
	salary=pd.read_csv('DKSalaries.cs')
	[players, cols]=salary.shape
	for index, row in salary.iterrows():
		if row.Position in ['QB', 'WR', 'TE', 'RB']:
			position_csv=pd.read_csv('merged_data/merged'+row.Position+'.csv')
			player=position_csv[position_csv.player==row.Name]
			fp=player['Fantasy Points'].mean()
			salary.set_value(index, 'Fantasy Points', fp)
		else:
			salary.set_value(index, 'Fantasy Points', row['AvgPointsPerGame'])
		print index/players*100
			 
	salary.to_csv('new_salary.csv')

def merge():
	files=os.listdir('Week3/data')
	print files
	for file in files:
		if 'DST' in file:
			continue
		position=file[0:file.index('.')]
		print position
		df=pd.read_csv('Week3/data/'+file)
		print "Merging data for " + position
		if position=='QB':
			ffpoints=4*df['passTds']+.04*df['passYds']-df['passInt']+.1*df['rushYds']+6*df['rushTds']-df['fumbles']+2*df['twoPts']
			passing_bonus=np.where(df['passYds']>=300, 3,0)
			total_pts=ffpoints+passing_bonus
		elif position=='RB':
			rushing_bonus=np.where(df['rushYds']>=100,3,0)
			receiving_bonus=np.where(df['recYds']>=100,3,0)
			total_pts=.1*df['rushYds']+6*df['rushTds']+6*df['returnTds']+6*df['recTds']+df['rec']-df['fumbles']+.1*df['recYds']+rushing_bonus+receiving_bonus
		elif position=='WR':
			rushing_bonus=np.where(df['rushYds']>=100,3,0)
			receiving_bonus=np.where(df['recYds']>=100,3,0)
			total_pts=.1*df['rushYds']+6*df['rushTds']+6*df['returnTds']+6*df['recTds']-df['fumbles']+df['rec']+.1*df['recYds']+rushing_bonus+receiving_bonus
		elif position=='TE':
			receiving_bonus=np.where(df['recYds']>=100,3,0)
			total_pts=df['rec']+.1*df['recYds']+.1*df['rushYds']+6*df['rushTds']+6*df['returnTds']+6*df['recTds']-df['fumbles']+receiving_bonus
		else: #Must be DST team
			#df['dstBlk'].fillna(0,inplace=True)
			total_pts=2*df['dstInt']+2*df['dstFumlRec']+df['dstSack']+6*df['dstTd']+2*df['dstSafety']+2*df['dstBlk']+6*df['dstRetTd']
			df.set_value(df[(df['dstPtsAllow']>=0) &( df['dstPtsAllow']<.5)].index, 'points', 10)
			df.set_value(df[(df['dstPtsAllow']>=.5) &( df['dstPtsAllow']<6.5)].index, 'points', 7)
			df.set_value(df[(df['dstPtsAllow']>=6.5) &( df['dstPtsAllow']<13.5)].index, 'points', 4)
			df.set_value(df[(df['dstPtsAllow']>=13.5) &( df['dstPtsAllow']<20.5)].index, 'points', 1)
			df.set_value(df[(df['dstPtsAllow']>=20.5) &( df['dstPtsAllow']<27.5)].index, 'points', 0)
			df.set_value(df[(df['dstPtsAllow']>=27.5) &( df['dstPtsAllow']<34.5)].index, 'points', -1)
			df.set_value(df[(df['dstPtsAllow']>=34.5)]['points'].index, 'points', -4)
			total_pts=total_pts+df['points']
		df['Fantasy Points']=total_pts
		df.to_csv('new'+file)
		columns=df.columns
		merged_df=pd.DataFrame(columns=columns)
		first_playerId=df['playerId'][0]
		#Calculate how many players there must be in first projection
		first_player_projections=df[df['playerId']==first_playerId]
		indices=first_player_projections.index
		num_players=indices[1]-indices[0]#indices[0]

		for i in xrange(num_players):
			#Grab the player, then all projections with that player
			player=df.iloc[i]
			player_projections=df[df.playerId==player.playerId]
			#Merged them
			player_merged=player_projections.mean()
			player_merged['player']=player.player
			player_merged['position']=player.position
			masked_fp=np.ma.array(player_projections['Fantasy Points'], mask=np.isnan(player_projections['Fantasy Points']))
			deviation=np.nanstd(player_projections['Fantasy Points'])
			#deviation=player_projections['Fantasy Points'].std(ddof = 1, skipna=True)
			player_merged['FP deviation']=deviation
			player_merged['Ceiling']=player_merged['Fantasy Points']+2*player_merged['FP deviation']
			player_merged['Floor']=player_merged['Fantasy Points']-2*player_merged['FP deviation']
			player_merged['Geometric mean']=scistats.gmean(masked_fp)
			player_merged['Median']=np.nanmedian(player_projections['Fantasy Points'])
			merged_df=merged_df.append(player_merged, ignore_index=True)
			# merged_df.iloc[i].player=player.player
			# merged_df.iloc[i].position=player.position
			merged_df=merged_df.drop(['Unnamed: 0', 'analyst'], axis=1)
		merged_df=merged_df.sort_values('Fantasy Points', ascending=False)

		new_file='merged'+position+'.csv'
		new_file2='merged_smaller'+position+'.csv'
		#merged_df.to_csv(new_file, index=False)
		merged_df.to_csv(new_file2, columns=['player', 'position', 'Fantasy Points', 'FP deviation', 'Floor', 'Ceiling', 'Geometric mean', 'Median'])
		os.rename(new_file2, 'Week3/'+new_file2 )
		print new_file2

def merge_merges():
	files=os.listdir('Week3/')
	dataframes=[]
	print "building"
	columns=['player', 'position', 'Fantasy Points', 'FP deviation', 'Floor', 'Ceiling', 'Geometric mean', 'Median']
	headers=['Player', 'Position', 'Fantasy Points', 'FP Deviation']
	for file in files:
		if 'smaller' in file:
 			df=pd.read_csv('Week3/'+file)
			dataframes.append(df)
	merged = pd.concat(dataframes)
	for col in merged.columns:
		if 'Unnamed' in col:
			del merged[col]
	merged.drop(merged.columns[0], axis=1)
	merged.to_csv('merged_projections_Week3_corrected_newstats.csv', index=False )

def merge_actual():
	files=os.listdir('actual/')
	dataframes=[]
	for index, file in enumerate(files):
		print file
		if '.DS' in file:
			continue
		df=pd.read_csv('actual/'+file)
		dataframes.append(df)
	merged=pd.concat(dataframes)
	# for col in merged.columns:
	# 	if 'Unnamed' in col:
	# 		del merged[col]

	merged.to_csv('merged_offense.csv')

def clean_merged_actual():
	df=pd.read_csv('merged_offense.csv')
	for index, row in df.iterrows():
		if row[1]=='FPts' and index>2:
			df.drop(index, inplace=True) 
			print "deleting"
	df.to_csv('mergx.csv')
if __name__ == '__main__':
	merge()
	merge_merges()
	#clean_merged_actual()
 
 