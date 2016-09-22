import pandas
import os
import sys
global years
years=['2013','2014','2015']
#weather only
def clean_names():
	years=['2013','2014','2015']
	for year in years:
		filename='NFLWeatherData'+year+'.csv'
		f2='NFLWeatherDataCleaned'+year+'.csv'
		weather=pandas.read_csv('Weather/'+filename)
		print("cleaning names")
		homes=weather['Home Team']
		aways=weather['Away Team']
		weather['Home Team']=[name.replace('  ', ' ') for name in homes]
		weather['Away Team']=[name.replace('  ', ' ') for name in aways]
		weather.drop('Dew Point',1)
		weather.drop('Cloud Cover', 1)
		weather.drop('Preicipitation Prob',1)
		weather.to_csv(f2, index=False)


def add_opponents():
	files=os.listdir('./Raw Data')[1::]
	
	#os.chdir('/Users/Sakib/Desktop/Projects/Fantasy Football Optimization/Data/Special Teams/2015')
	for file in files:
		print(file)
		#os.chdir('/Users/Sakib/Desktop/Projects/Fantasy Football Optimization/Data/Special Teams/2015')
		os.chdir('/Users/Sakib/Desktop/Projects/Fantasy-Football-Optimization/Scripts/Raw Data')
		length=len(file)
		year=file[length-8:length-4]
		index1=file.index('Week')
		index1=index1+4
		index2=file.index(year)
		week=file[index1:index2]
		print("reading csv")
		#Combine the first two rows as one header
		df=pandas.read_csv(file, header=None)
		gen_hdr=df.iloc[0].fillna('').tolist()
		stats=df.iloc[1].tolist()
		headers=map(lambda a,b: a+b, gen_hdr, stats)
		df=df[2:] #Drop the first two header rows
		df.columns=headers
		df = df.reset_index(drop=True)
		games, opponent_teams,player_teams=find_opponent(df['Team'], week, year)

		#df['Home or Away']=games
		#df['Opponent']=opponent_teams
		df['Home or Away']=games
		df['Opponent']=opponent_teams
		df['Team']=player_teams
		df.to_csv(file,index=False)


def find_opponent(teams, week,year):
	abr_teams=['ARI', 'ATL' ,'BAL' ,'BUF' ,'CAR', 'CHI' ,'CIN' ,'CLE', 'DAL' ,'DEN','DET' ,'GB' ,'HOU' ,'IND', 'JAC','KC', 'MIA', 'MIN','NE', 'NO' ,'NYG', 'NYJ' ,'OAK' ,'PHI', 'PIT' ,'SD', 'SF', 'SEA','STL','TB' ,'TEN', 'WAS' ]
	full_teams=['Arizona Cardinals', 'Atlanta Falcons', 'Baltimore Ravens', 'Buffalo Bills', 'Carolina Panthers', 'Chicago Bears', 'Cincinnati Bengals', 'Cleveland Browns', 'Dallas Cowboys', 'Denver Broncos', 'Detroit Lions', 'Green Bay Packers', 'Houston Texans', 'Indianapolis Colts', 'Jacksonville Jaguars', 'Kansas City Chiefs', 'Miami Dolphins', 'Minnesota Vikings', 'New England Patriots', 'New Orleans Saints', 'New York Giants', 'New York Jets', 'Oakland Raiders', 'Philadelphia Eagles', 'Pittsburgh Steelers', 'San Diego Chargers', 'San Francisco 49ers', 'Seattle Seahawks', 'St. Louis Rams', 'Tampa Bay Buccaneers', 'Tennessee Titans', 'Washington Redskins']
	filename='NFLWeatherDataCleaned'+year+'.csv'
	opponent_teams=[]
	games=[]
	player_teams=[]
	os.chdir('../../Data/Weather/')
	schedule=pandas.read_csv(filename)
	relevant_schedule=schedule.loc[schedule['Week']==int(week)]
	for team in teams:
		# print("Checking teams")
		# print(team)
		#convert the abbreviated team name to full
		player_team=full_teams[abr_teams.index(team)]
		player_teams.append(player_team)
		#print('Team:'+team)
		#Check if player is playing at home or away
		if player_team in relevant_schedule['Home Team'].values:
			games.append('Home')
			opponent_teams.append(relevant_schedule[relevant_schedule['Home Team']==player_team]['Away Team'].item())
		else:
			games.append('Away')
			opponent_teams.append(relevant_schedule[relevant_schedule['Away Team']==player_team]['Home Team'].item())
	return games, opponent_teams, player_teams

def add_week():
	positions=['QB', 'RB', 'WR', 'TE']

	for year in years:
		for position in positions:
			path='/Users/Sakib/Desktop/Projects/Fantasy-Football-Optimization/Data/Cleaned/Player Stats/'+year
			files=os.listdir(path)
			files=list(filter(lambda x: position in x, files))		
			for file in files:
				df=pandas.read_csv(path+'/'+file)
				index1=file.index('Week')
				index1=index1+4
				index2=file.index(year)
				week=file[index1:index2]
				print(week)
				print(file)
				df['Week']=int(week)
				df.to_csv(path+'/'+file, index=False)		

def merge_csv():
	positions=['QB', 'RB', 'WR', 'TE']
	for year in years:
		for position in positions:
			df_list = []
			path='/Users/Sakib/Desktop/Projects/Fantasy-Football-Optimization/Data/Cleaned/Player Stats/'+year
			files=os.listdir(path)
			files=list(filter(lambda x: position in x, files))		
			filename=position+year+'.csv'

			for file in files:
				print(file)
				df_list.append(pandas.read_csv(path+'/'+file))
			print("Appended")
			full_df=pandas.concat(df_list)
			full_df.to_csv(filename, index=False)


if __name__ == '__main__':
	#clean_names()
	#add_opponents()
	add_week()
	merge_csv()