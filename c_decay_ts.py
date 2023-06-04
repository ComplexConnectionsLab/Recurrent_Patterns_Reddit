import sqlite3
import pandas as pd
import pytz
import json
from datetime import datetime
from tqdm import tqdm
import numpy as np
def create_data(database,output_data,select_posts,year_week,freq,max_number):
	#sentiment
	est = pytz.timezone('US/Eastern')
	utc_tmzone = pytz.utc
	#sqlite
	def dict_factory(cursor, row):
		d = {}
		for idx, col in enumerate(cursor.description):
			d[col[0]] = row[idx]
		return d
	#post
	conn = sqlite3.connect("./data/"+database+".db")
	conn.row_factory = dict_factory
	c = conn.cursor()
	c.execute(select_posts.format(year = str(year_week[0]), week = str(year_week[1])))
	posts = []
	for post in c:
		if post["text"] == "[removed]":
			continue
		if post["author"].lower().endswith("bot"):
			continue
		if post["author"] == "AutoModerator":
			continue
		posts.append(post)
	key = str(year_week[0])+"_"+str(year_week[1])
	df_posts = pd.DataFrame(posts)
	df_posts["num_comments"] = pd.to_numeric(df_posts["num_comments"])
	df_posts = df_posts.sort_values(by = ["num_comments"])
	df_posts = df_posts.tail(100)
	output_data[key] = {}
	#comments
	select_comms = "SELECT * FROM comments WHERE id_submission = '{id_link}'"
	temp_ld = []
	for _,post in df_posts.iterrows():
		c.execute(select_comms.format(id_link = post["id_submission"]))
		t0 = int(post["utc"])
		temp_ld.append({
		"interactions":1,
		"time": datetime.fromtimestamp(int(post["utc"]),tz = utc_tmzone)
		})
		for comm in c:
			if comm["text"] == "[removed]":
				continue
			if post["author"].lower().endswith("bot"):
				continue
			if post["author"] == "AutoModerator":
				continue
			dt = int(comm["utc"]) - int(post["utc"])
			if dt > 86400:
				continue
			temp_ld.append({
			"interactions":1,
			"time":datetime.fromtimestamp(int(comm["utc"]),tz = utc_tmzone)
			})
		df = pd.DataFrame(temp_ld)
		df = df.sort_values(by = ["time"])
		aggdf = df.groupby(pd.Grouper(freq = freq,key = 'time')).interactions.sum().reset_index()
		aggdf["cum_sum"] = aggdf["interactions"].cumsum()
		m = aggdf["cum_sum"].max()
		aggdf["cum_sum"] /= m
		id = aggdf[aggdf["cum_sum"]>0.7].index.tolist()[0]
		time_decay_threshold = int(aggdf.loc[id,"time"].timestamp())
		data_init = int(aggdf.loc[0,"time"].timestamp())
		delta_t = time_decay_threshold-data_init
		output_data[key][post["id_submission"]] = {}
		output_data[key][post["id_submission"]]["data"] = delta_t
		output_data[key][post["id_submission"]]["num_comments"] = int(post["num_comments"])
	conn.close()
def create_trees(database):
	year_weeks = [(2020,i) for i in range(1,54)]
	for i in range(1,5):
		year_weeks.append((2021,i))
	select_posts = "SELECT * FROM submissions WHERE year == '{year}' and week == '{week}'"
	output_data = {}
	for year_week in tqdm(year_weeks):
		create_data(database,output_data,select_posts,year_week,"5min",24*12)
	with open("data/ts_interactions/decay_"+database+".json","w") as outpuf:
		json.dump(output_data,outpuf)
create_trees("wsb")
