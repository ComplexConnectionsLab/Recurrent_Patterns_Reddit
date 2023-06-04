import pytz
from datetime import datetime,timedelta
import pandas as pd
from scipy.stats import skew
import numpy as np
import seaborn as sns
import json
#
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.dates as mdates
matplotlib.use('Cairo')
matplotlib.style.use("fast")
#bigrams

def get_ngrams(kind):
	year_weeks = ["2020_"+str(i) for i in range(1,54)]
	for i in range(1,5):
		year_weeks.append("2021_"+str(i))
	patterns = {}
	tmp_week = {}
	id_pattern = 0
	xs = []
	for year_week in year_weeks:
		with open("data/ngrams/"+kind+"_"+year_week+".csv","r") as inpuf:
			df = pd.read_csv(inpuf)
		z_scores = []
		for _,row in df.iterrows():
			yt = row[[str(y) for y in range(100)]]
			if yt.std() == 0.0:
				continue
			z_score = (row["how_many_times"]-yt.mean())/yt.std()
			z_scores.append({"pattern":row["pattern"],"z_score":z_score})
		z_df = pd.DataFrame(z_scores)
		z_df = z_df.sort_values(by = ["z_score"],ascending = False)
		how_many = int(z_df.shape[0]*0.15)
		z_df = z_df.head(how_many)
		z_scores = {}
		for _,row in z_df.iterrows():
			z_scores[row["pattern"]] = row["z_score"]
			if row["pattern"] not in patterns:
				patterns[row["pattern"]] = id_pattern
				id_pattern +=1
		tmp_week[year_week] = z_scores
		xs.append(datetime.strptime(year_week + '-1', "%Y_%W-%w"))
	#normalize data
	week_data = {}
	for (week,data) in tmp_week.items():
		week_data[week] = np.zeros(id_pattern)
		for (pattern,z_score) in data.items():
			week_data[week][patterns[pattern]] = z_score
		norm = np.linalg.norm(week_data[week])
		week_data[week] = week_data[week]/norm
	tmp = np.array([v for v in week_data.values()])
	pairwise_similarity = tmp.dot(tmp.T)
	ts = [pairwise_similarity[x-1,x] for x in range(1, len(year_weeks))]
	xs = xs[1:]
	yws = year_weeks[1:]
	return xs,ts,yws

def save_radar_not_events(kind):
	est = pytz.timezone('US/Eastern')
	utc_tmzone = pytz.utc
	tmp = {
			#us
			"Trump Covid":datetime(2020,10,2),
			"Trump":datetime(2020,2,5),
			"US 2020":datetime(2020,11,3),
			"Capitol Hill":datetime(2021,1,6),
			"BLM":datetime(2020,6,6),
			#covid-19
			"Coronavirus":datetime(2020,3,11),
			"Lockdown Ease":datetime(2020,5,1),
			#eu
			"Brexit":datetime(2020,1,31),
			"Belarus Protest":datetime(2020,8,10),
			"Cyprus":datetime(2020,9,10),
			#March 11 – COVID-19 pandemic: The World Health Organization declares the COVID-19 outbreak a pandemic.[51]
			#nba
			"Orlando":datetime(2020,7,31),
			"NBA Finals":datetime(2020,10,11),
			"NBA Trades":datetime(2020,11,21),
			"Kobe Bryant":datetime(2020,1,26),
			"NBA Stop":datetime(2020,3,12),
			"NBA Restart":datetime(2020,12,22),
			#nfl
			"NFL Draft":datetime(2020,4,24),
			"NFL Kickoff Game":datetime(2020,9,11),
			"SuperBowl LIV":datetime(2020,2,2),
			"NFL Trades":datetime(2020,3,18),
			"NFL PlayOff":datetime(2021,1,10),
		}
	dict_reddit_events = {
						"europe": ["Brexit","Cyprus","Belarus Protest","Lockdown Ease","US 2020","Capitol Hill","Coronavirus"],
						"politics": ["Trump","Trump Covid","US 2020","Capitol Hill","Coronavirus","BLM"],
						"nba":["Kobe Bryant","NBA Stop","NBA Restart","Orlando","NBA Finals","NBA Trades"],
						"nfl":["NFL Draft","NFL Kickoff Game","SuperBowl LIV","NFL Trades","NFL PlayOff"]
						}
	dict_event = {}
	dict_events = {}
	dict_events_all = {}
	for (k,v) in tmp.items():
		v.replace(tzinfo = utc_tmzone)
		v = v-timedelta(days = 7)
		year = v.year
		week = v.isocalendar()[1]
		if str(year)+"_"+str(week) == "2021_1":
			dict_events[k] = ["2020_53"]
		else:
			dict_events[k] = [str(year)+"_"+str(week)]
		dict_event[k] = v
		v_1 = v-timedelta(days = 7)
		year = v_1.year
		week = v_1.isocalendar()[1]
		if str(year)+"_"+str(week) == "2020_53":
			dict_events[k].append("2020_52")
		elif str(year)+"_"+str(week) == "2021_53":
			dict_events[k].append("2020_53")
		else:
			dict_events[k].append(str(year)+"_"+str(week))
		#for posts
		v_1 = v+timedelta(days = 4)
		v_2 = v-timedelta(days = 4)
		dict_events_all[k] = [v_1,v_2]
	dict_events["Capitol Hill"] = ["2020_51","2020_50"]
	dict_events["NFL PlayOff"] = ["2020_51","2020_50"]
	#metrics
	metrics = []
	#number_of_posts
	with open("data/basic_stats/"+kind+".csv","r") as inpuf:
		df = pd.read_csv(inpuf,sep = ";")
	df["tdate"] = df.apply(lambda x: datetime(int(x["date"].split("_")[0]),int(x["date"].split("_")[1]),int(x["date"].split("_")[2])), axis = 1)
	df = df.sort_values(by = ["tdate"])
	df = df.drop_duplicates(subset = ["tdate"])
	N = len(dict_reddit_events[kind])
	for i in range(0,N):
		event = dict_reddit_events[kind][i]
		dates = dict_events_all[event]
		tdf = df[(df["tdate"].dt.date>dates[1].date())&(df["tdate"].dt.date<dates[0].date())]
		#maybe something here. change scale!! (confronto tra subreddits differente)
		#tdf["posts"] = (tdf["posts"]-tdf["posts"].min())/(tdf["posts"].max()-tdf["posts"].min())
		y = tdf["posts"].tolist()
		metrics.append({"metric":"posts","subreddit":kind,"event":event,"value":y[3]})
	#distrib dt
	with open("data/distribution/interactions_"+kind+".json","r") as inpuf:
		data = json.load(inpuf)
	ndata = []
	for (k,ls) in data.items():
		ys = np.array(ls)
		ys = ys/3600
		r = datetime.strptime(k + '-1', "%Y_%W-%w")
		m = skew(ys)
		ndata.append({
					"date":r,
					"y":m,
					"string_yw":k
					})
	df = pd.DataFrame(ndata)
	df = df.sort_values(by = ["date"])
	df = df.drop_duplicates(subset = ["date"])
	for event in dict_reddit_events[kind]:
		dates = dict_events[event]
		event_value = df[df["string_yw"] == dates[0]].iloc[0]["y"]
		week_before = df[df["string_yw"] == dates[1]].iloc[0]["y"]
		delta_y = event_value
		metrics.append({"metric":"skew_dt","subreddit":kind,"event":event,"value":delta_y})
	#dtw
	with open("data/ts_week_after/dtw_interactions_"+kind+".json","r") as inpuf:
		data = json.load(inpuf)
	ndata = []
	for (k,ls) in data.items():
		m = np.mean(ls)
		r = datetime.strptime(k + '-1', "%Y_%W-%w")
		ndata.append({"date":r,"mean":m,"string_yw":k})
	df = pd.DataFrame(ndata)
	df = df.sort_values(by = ["date"])
	df = df.drop_duplicates(subset = ["date"])
	for event in dict_reddit_events[kind]:
		dates = dict_events[event]
		event_value = df[df["string_yw"] == dates[0]].iloc[0]["mean"]
		week_before = df[df["string_yw"] == dates[1]].iloc[0]["mean"]
		delta_y = event_value
		metrics.append({"metric":"dtw","subreddit":kind,"event":event,"value":delta_y})
	#coherence
	with open("data/ts_week_after/coherence_interactions_"+kind+".json","r") as inpuf:
		data = json.load(inpuf)
	ndata = []
	for (k,ls) in data.items():
		if k == "f":
			continue
		ys = np.array(ls)
		coherences_week = np.array(ls)
		removed_zero_coh = coherences_week[:,1:]
		means_over_omega = np.mean(removed_zero_coh,axis = 1)
		true_mean = np.mean(means_over_omega)
		r = datetime.strptime(k + '-1', "%Y_%W-%w")
		ndata.append({"date":r,"mean":true_mean,"string_yw":k})
	df = pd.DataFrame(ndata)
	df = df.sort_values(by = ["date"])
	df = df.drop_duplicates(subset = ["date"])
	for event in dict_reddit_events[kind]:
		dates = dict_events[event]
		event_value = df[df["string_yw"] == dates[0]].iloc[0]["mean"]
		week_before = df[df["string_yw"] == dates[1]].iloc[0]["mean"]
		delta_y = event_value
		metrics.append({"metric":"coherence","subreddit":kind,"event":event,"value":delta_y})
	#compression
	with open("data/ts_interactions/compression_"+kind+".json","r") as inpuf:
		data = json.load(inpuf)
	ndata = []
	for (k,ls) in data.items():
		ys = np.array([l for (sub,l) in ls.items()])
		r = datetime.strptime(k + '-1', "%Y_%W-%w")
		ndata.append({
					"date":r,
					"mean":np.mean(ys),
					"string_yw":k
					})
	df = pd.DataFrame(ndata)
	df = df.sort_values(by = ["date"])
	df = df.drop_duplicates(subset = ["date"])
	for event in dict_reddit_events[kind]:
		dates = dict_events[event]
		event_value = df[df["string_yw"] == dates[0]].iloc[0]["mean"]
		week_before = df[df["string_yw"] == dates[1]].iloc[0]["mean"]
		delta_y = event_value
		metrics.append({"metric":"compression","subreddit":kind,"event":event,"value":delta_y})
	# bigrams
	xs,ts,yws = get_ngrams(kind)
	df =  pd.DataFrame()
	df["date"] = xs
	df["value"] = ts
	df["string_yw"] = yws
	df = df.sort_values(by = ["date"])
	df = df.drop_duplicates(subset = ["date"])
	for event in dict_reddit_events[kind]:
		dates = dict_events[event]
		event_value = df[df["string_yw"] == dates[0]].iloc[0]["value"]
		week_before = df[df["string_yw"] == dates[1]].iloc[0]["value"]
		delta_y = event_value
		metrics.append({"metric":"bigrams","subreddit":kind,"event":event,"value":delta_y})
	#sentiment
	with open("data/to_plot/area_sentiment.csv","r") as inpuf:
		df = pd.read_csv(inpuf, sep = ",")
	dict_label = {"europe":"Europe","politics":"U.S. politics","nfl":"NFL","nba":"NBA"}
	df = df[df["kind"] == dict_label[kind]]
	df = df[df["is_event"] == "No"]
	for event in dict_reddit_events[kind]:
		xdf = df[df["event_name"] == dict_events[event][0]].iloc[0]["value"]
		metrics.append({"metric":"sentiment","subreddit":kind,"event":event,"value":xdf})
	#output
	output = pd.DataFrame(metrics)
	output.to_csv("data/to_plot/radar_not_events_"+kind+".csv",sep = ",",index = False)
#save radar
def save_radar(kind):
	est = pytz.timezone('US/Eastern')
	utc_tmzone = pytz.utc
	tmp = {
			#us
			"Trump Covid":datetime(2020,10,2),
			"Trump":datetime(2020,2,5),
			"US 2020":datetime(2020,11,3),
			"Capitol Hill":datetime(2021,1,6),
			"BLM":datetime(2020,6,6),
			#covid-19
			"Coronavirus":datetime(2020,3,11),
			"Lockdown Ease":datetime(2020,5,1),
			#eu
			"Brexit":datetime(2020,1,31),
			"Belarus Protest":datetime(2020,8,10),
			"Cyprus":datetime(2020,9,10),
			#March 11 – COVID-19 pandemic: The World Health Organization declares the COVID-19 outbreak a pandemic.[51]
			#nba
			"Orlando":datetime(2020,7,31),
			"NBA Finals":datetime(2020,10,11),
			"NBA Trades":datetime(2020,11,21),
			"Kobe Bryant":datetime(2020,1,26),
			"NBA Stop":datetime(2020,3,12),
			"NBA Restart":datetime(2020,12,22),
			#nfl
			"NFL Draft":datetime(2020,4,24),
			"NFL Kickoff Game":datetime(2020,9,11),
			"SuperBowl LIV":datetime(2020,2,2),
			"NFL Trades":datetime(2020,3,18),
			"NFL PlayOff":datetime(2021,1,10),
		}
	dict_events = {}
	for (k,v) in tmp.items():
		v.replace(tzinfo = utc_tmzone)
		dict_events[k] = v
	dict_reddit_events = {
						"europe": ["Brexit","Cyprus","Belarus Protest","Lockdown Ease","US 2020","Capitol Hill","Coronavirus"],
						"politics": ["Trump","Trump Covid","US 2020","Capitol Hill","Coronavirus","BLM"],
						"nba":["Kobe Bryant","NBA Stop","NBA Restart","Orlando","NBA Finals","NBA Trades"],
						"nfl":["NFL Draft","NFL Kickoff Game","SuperBowl LIV","NFL Trades","NFL PlayOff"]
						}
	dict_event = {}
	dict_events = {}
	dict_events_all = {}
	for (k,v) in tmp.items():
		v.replace(tzinfo = utc_tmzone)
		year = v.year
		week = v.isocalendar()[1]
		if str(year)+"_"+str(week) == "2021_1":
			dict_events[k] = ["2020_53"]
		else:
			dict_events[k] = [str(year)+"_"+str(week)]
		dict_event[k] = v
		v_1 = v-timedelta(days = 7)
		year = v_1.year
		week = v_1.isocalendar()[1]
		if str(year)+"_"+str(week) == "2020_53":
			dict_events[k].append("2020_52")
		elif str(year)+"_"+str(week) == "2021_53":
			dict_events[k].append("2020_53")
		else:
			dict_events[k].append(str(year)+"_"+str(week))
		v_1 = v+timedelta(days = 4)
		v_2 = v-timedelta(days = 4)
		dict_events_all[k] = [v_1,v_2]
	#metrics
	metrics = []
	#number_of_posts
	with open("data/basic_stats/"+kind+".csv","r") as inpuf:
		df = pd.read_csv(inpuf,sep = ";")
	df["tdate"] = df.apply(lambda x: datetime(int(x["date"].split("_")[0]),int(x["date"].split("_")[1]),int(x["date"].split("_")[2])), axis = 1)
	df = df.sort_values(by = ["tdate"])
	df = df.drop_duplicates(subset = ["tdate"])
	N = len(dict_reddit_events[kind])
	for i in range(0,N):
		event = dict_reddit_events[kind][i]
		dates = dict_events_all[event]
		tdf = df[(df["tdate"].dt.date>dates[1].date())&(df["tdate"].dt.date<dates[0].date())]
		#as before
		#tdf["posts"] = (tdf["posts"]-tdf["posts"].min())/(tdf["posts"].max()-tdf["posts"].min())
		y = tdf["posts"].tolist()
		metrics.append({"metric":"posts","subreddit":kind,"event":event,"value":y[3]})
	#distrib dt
	with open("data/distribution/interactions_"+kind+".json","r") as inpuf:
		data = json.load(inpuf)
	ndata = []
	for (k,ls) in data.items():
		ys = np.array(ls)
		ys = ys/3600
		r = datetime.strptime(k + '-1', "%Y_%W-%w")
		m = skew(ys)
		ndata.append({
					"date":r,
					"y":m,
					"string_yw":k
					})
	df = pd.DataFrame(ndata)
	df = df.sort_values(by = ["date"])
	df = df.drop_duplicates(subset = ["date"])
	for event in dict_reddit_events[kind]:
		dates = dict_events[event]
		event_value = df[df["string_yw"] == dates[0]].iloc[0]["y"]
		week_before = df[df["string_yw"] == dates[1]].iloc[0]["y"]
		delta_y = event_value
		metrics.append({"metric":"skew_dt","subreddit":kind,"event":event,"value":delta_y})
	#dtw
	with open("data/ts_week_after/dtw_interactions_"+kind+".json","r") as inpuf:
		data = json.load(inpuf)
	ndata = []
	for (k,ls) in data.items():
		m = np.mean(ls)
		r = datetime.strptime(k + '-1', "%Y_%W-%w")
		ndata.append({"date":r,"mean":m,"string_yw":k})
	df = pd.DataFrame(ndata)
	df = df.sort_values(by = ["date"])
	df = df.drop_duplicates(subset = ["date"])
	for event in dict_reddit_events[kind]:
		dates = dict_events[event]
		event_value = df[df["string_yw"] == dates[0]].iloc[0]["mean"]
		week_before = df[df["string_yw"] == dates[1]].iloc[0]["mean"]
		delta_y = event_value
		metrics.append({"metric":"dtw","subreddit":kind,"event":event,"value":delta_y})
	#coherence
	with open("data/ts_week_after/coherence_interactions_"+kind+".json","r") as inpuf:
		data = json.load(inpuf)
	ndata = []
	for (k,ls) in data.items():
		if k == "f":
			continue
		ys = np.array(ls)
		coherences_week = np.array(ls)
		removed_zero_coh = coherences_week[:,1:]
		means_over_omega = np.mean(removed_zero_coh,axis = 1)
		true_mean = np.mean(means_over_omega)
		r = datetime.strptime(k + '-1', "%Y_%W-%w")
		ndata.append({"date":r,"mean":true_mean,"string_yw":k})
	df = pd.DataFrame(ndata)
	df = df.sort_values(by = ["date"])
	df = df.drop_duplicates(subset = ["date"])
	for event in dict_reddit_events[kind]:
		dates = dict_events[event]
		event_value = df[df["string_yw"] == dates[0]].iloc[0]["mean"]
		week_before = df[df["string_yw"] == dates[1]].iloc[0]["mean"]
		delta_y = event_value
		metrics.append({"metric":"coherence","subreddit":kind,"event":event,"value":delta_y})
	#compression
	with open("data/ts_interactions/compression_"+kind+".json","r") as inpuf:
		data = json.load(inpuf)
	ndata = []
	for (k,ls) in data.items():
		ys = np.array([l for (sub,l) in ls.items()])
		r = datetime.strptime(k + '-1', "%Y_%W-%w")
		ndata.append({
					"date":r,
					"mean":np.mean(ys),
					"string_yw":k
					})
	df = pd.DataFrame(ndata)
	df = df.sort_values(by = ["date"])
	df = df.drop_duplicates(subset = ["date"])
	for event in dict_reddit_events[kind]:
		dates = dict_events[event]
		event_value = df[df["string_yw"] == dates[0]].iloc[0]["mean"]
		week_before = df[df["string_yw"] == dates[1]].iloc[0]["mean"]
		delta_y = event_value
		metrics.append({"metric":"compression","subreddit":kind,"event":event,"value":delta_y})
	# bigrams
	xs,ts,yws = get_ngrams(kind)
	df =  pd.DataFrame()
	df["date"] = xs
	df["value"] = ts
	df["string_yw"] = yws
	df = df.sort_values(by = ["date"])
	df = df.drop_duplicates(subset = ["date"])
	for event in dict_reddit_events[kind]:
		dates = dict_events[event]
		event_value = df[df["string_yw"] == dates[0]].iloc[0]["value"]
		week_before = df[df["string_yw"] == dates[1]].iloc[0]["value"]
		delta_y = event_value
		metrics.append({"metric":"bigrams","subreddit":kind,"event":event,"value":delta_y})
	#sentiment
	with open("data/to_plot/area_sentiment.csv","r") as inpuf:
		df = pd.read_csv(inpuf, sep = ",")
	dict_label = {"europe":"Europe","politics":"U.S. politics","nfl":"NFL","nba":"NBA"}
	df = df[df["kind"] == dict_label[kind]]
	df = df[df["is_event"] == "Yes"]
	for event in dict_reddit_events[kind]:
		xdf = df[df["event_name"] == event].iloc[0]["value"]
		metrics.append({"metric":"sentiment","subreddit":kind,"event":event,"value":xdf})
	#output
	output = pd.DataFrame(metrics)
	output.to_csv("data/to_plot/radar_"+kind+".csv",sep = ",",index = False)


save_radar_not_events("politics")
save_radar("politics")
