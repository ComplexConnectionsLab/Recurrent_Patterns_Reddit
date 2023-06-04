import warnings
warnings.filterwarnings('error')
import json
import pandas as pd
from scipy import signal
from tqdm import tqdm
from itertools import product

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
			try:
				f, Cxy = signal.coherence(y1, y2, fs = 10**3, nperseg = 48, noverlap = 24)
			except Warning:
				continue
			output_data[key_2].append(Cxy.tolist())
	output_data["f"] = f.tolist()
	with open("data/ts_week_after/coherence_sentiment_"+database+".json","w") as outpuf:
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
			try:
				f, Cxy = signal.coherence(y1, y2, fs = 10**3, nperseg = 48, noverlap = 24)
			except Warning:
				continue
			output_data[key_2].append(Cxy.tolist())
	output_data["f"] = f.tolist()
	with open("data/ts_week_after/coherence_interactions_"+database+".json","w") as outpuf:
		json.dump(output_data,outpuf)

create_data_sentiment("ukpolitics")
create_data_interactions("ukpolitics")
