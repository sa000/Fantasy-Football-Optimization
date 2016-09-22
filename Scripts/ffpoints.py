import pandas
import os
import numpy as np
def calculation():
	path='/Users/Sakib/Desktop/Projects/Fantasy-Football-Optimization/Data/Merged'
	files=os.listdir(path)
	os.chdir(path)
	for file in files:
		position=file[0:2]
		df=pandas.read_csv(file)
		if position=='QB':
			calculation=4*df['PassingTD']+.04*df['PassingYard']-df['PassingINT']+.1*df['RushingYard']+6*df['RushingTD']
			passing_bonus=np.where(df['PassingYard']>=300, 3,0)
			total_pts=calculation+passing_bonus
		elif position=='RB':
			rushing_bonus=np.where(df['RushingYard']>=100,3,0)
			receiving_bonus=np.where(df['ReceivingYard']>=100,3,0)
			total_pts=.1*df['RushingYard']+6*df['RushingTD']+df['ReceivingRec']+.1*df['ReceivingYard']+rushing_bonus+receiving_bonus
		elif position=='WR':
			rushing_bonus=np.where(df['RushingYard']>=100,3,0)
			receiving_bonus=np.where(df['ReceivingYard']>=100,3,0)
			total_pts=.1*df['RushingYard']+6*df['ReceivingTD']+df['ReceivingRec']+.1*df['ReceivingYard']+rushing_bonus+receiving_bonus
		else:
			receiving_bonus=np.where(df['ReceivingYard']>=100,3,0)
			total_pts=df['ReceivingRec']+.1*df['ReceivingYard']+6*df['ReceivingTD']+receiving_bonus
		df['Actual Fantasy Points Scored']=total_pts
		df.to_csv(file,index=False)

if __name__ == '__main__':
	calculation()