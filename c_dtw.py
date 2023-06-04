import json
import pandas as pd
from tqdm import tqdm
from itertools import product
import numpy as np
def DTWDistance(s1, s2):
	DTW={}

	for i in range(len(s1)):
		DTW[(i, -1)] = float('inf')
	for i in range(len(s2)):
		DTW[(-1, i)] = float('inf')
	DTW[(-1, -1)] = 0

	for i in range(len(s1)):
		for j in range(len(s2)):
			dist= (s1[i]-s2[j])**2
			DTW[(i, j)] = dist + min(DTW[(i-1, j)],DTW[(i, j-1)], DTW[(i-1, j-1)])

	return np.sqrt(DTW[len(s1)-1, len(s2)-1])

def create_data_sentiment(database):
	with open("data/ts_interactions/sentiment_"+database+".json","r") as inpuf:
		data_trees = json.load(inpuf)
	year_weeks = [(2020,i) for i in range(1,54)]
	for i in range(1,5):
		year_weeks.append((2021,i))
	seq_weeks = [[year_weeks[i],year_weeks[i+1]] for i in range(0,len(year_weeks)-1)]
	output_data = {}
	for seq_week in tqdm(seq_weeks):
		key_1 = str(seq_week[0][0])+"_"+str(seq_week[0][1])
		key_2 = str(seq_week[1][0])+"_"+str(seq_week[1][1])
		output_data[key_2] = []
		ts_1 = data_trees[key_1].keys()
		ts_2 = data_trees[key_2].keys()
		for c in product(ts_1,ts_2):
			y1 = data_trees[key_1][c[0]]["data"]
			y2 = data_trees[key_2][c[1]]["data"]
			Cxy = DTWDistance(y1, y2)
			output_data[key_2].append(Cxy)
	with open("data/ts_week_after/dtw_sentiment_"+database+".json","w") as outpuf:
		json.dump(output_data,outpuf)

def create_data_interactions(database):
	with open("data/ts_interactions/interactions_"+database+".json","r") as inpuf:
		data_trees = json.load(inpuf)
	year_weeks = [(2020,i) for i in range(1,54)]
	for i in range(1,5):
		year_weeks.append((2021,i))
	seq_weeks = [[year_weeks[i],year_weeks[i+1]] for i in range(0,len(year_weeks)-1)]
	output_data = {}
	for seq_week in tqdm(seq_weeks):
		key_1 = str(seq_week[0][0])+"_"+str(seq_week[0][1])
		key_2 = str(seq_week[1][0])+"_"+str(seq_week[1][1])
		output_data[key_2] = []
		ts_1 = data_trees[key_1].keys()
		ts_2 = data_trees[key_2].keys()
		for c in product(ts_1,ts_2):
			y1 = data_trees[key_1][c[0]]["data"]
			y2 = data_trees[key_2][c[1]]["data"]
			Cxy = DTWDistance(y1, y2)
			output_data[key_2].append(Cxy)
	with open("data/ts_week_after/dtw_interactions_"+database+".json","w") as outpuf:
		json.dump(output_data,outpuf)


create_data_interactions("ukpolitics")
create_data_sentiment("ukpolitics")

'''
europe
nba
politics
science
soccer
stocks
'''
