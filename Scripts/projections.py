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

def merge(week):
	files=os.listdir('Week%d/data' %week)
	dataframes=[]
	if '.DS_Store' in files:
		files.pop(0)
	for file in files:
		position=file[0:file.index('.')]
		print position
		df=pd.read_csv('Week%d/data/%s' % (week,file))
		df.fillna(0, inplace=True)
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
		df.set_value(df.index, 'Fantasy Points', total_pts) 
		df=df.drop(df[df['Fantasy Points']>100].index)
		#df.to_csv('new3'+file, columns=df.columns)
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
			merged_df.replace('--', 0, inplace=True)
		dataframes.append(merged_df)
	merged = pd.concat(dataframes)
	columns=['player', 'position', 'Fantasy Points', 'FP deviation', 'Floor', 'Ceiling', 'Geometric mean', 'Median']
	stat_columns=['Fantasy Points', 'FP deviation', 'Floor', 'Ceiling', 'Geometric mean', 'Median']
	for col in merged.columns:
		if 'Unnamed' in col:
			del merged[col]
	merged.drop(merged.columns[0], axis=1)
	merged['Geometric mean'].replace('--', 0, inplace=True)
 	merged[stat_columns]=np.round(merged[stat_columns].astype(float), decimals=2)
	merged.to_csv('merged_projections_Week%d_corrected_newstats.csv' %week, columns=columns, index=False )

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
	merged.replace('--', 0.0)
	merged.to_csv('merged_projections_Week3_corrected_newstats.csv', columns=columns, index=False )


def accumulate_csv():
	files=os.listdir('../Projections')
	merged_csvs=[]
	week=1
	print files
	for file in files:
		if '.csv' not in file:
			continue
		print file
		df=pd.read_csv('../Projections/'+file)
		df['Week']=week
		merged_csvs.append(df)
		week+=1
	merged=pd.concat(merged_csvs)
	merged.to_csv('Accumulated_projections.csv')

if __name__ == '__main__':
	#merge(1)
	accumulate_csv()
	#merge_merges()
	#clean_merged_actual()
 
 