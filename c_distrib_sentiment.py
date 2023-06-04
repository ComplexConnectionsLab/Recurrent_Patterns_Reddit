from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import sqlite3
import pandas as pd
import pytz
import json
from datetime import datetime
from tqdm import tqdm
def create_data(database,output_data,select_posts,year_week):
	#sentiment
	sia = SentimentIntensityAnalyzer()
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
	#get only TOP 100 by num comments
	df_posts = pd.DataFrame(posts)
	df_posts["num_comments"] = pd.to_numeric(df_posts["num_comments"])
	df_posts = df_posts.sort_values(by = ["num_comments"])
	df_posts = df_posts.tail(100)
	key = str(year_week[0])+"_"+str(year_week[1])
	output_data[key] = []
	#comments
	select_comms = "SELECT * FROM comments WHERE id_submission = '{id_link}'"
	for _,post in df_posts.iterrows():
		c.execute(select_comms.format(id_link = post["id_submission"]))
		output_data[key].append(sia.polarity_scores(post["title"].lower() + post["text"].lower())["compound"])
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
			output_data[key].append(sia.polarity_scores(comm["text"].lower())["compound"])
	conn.close()
def save_data(database):
	year_weeks = [(2020,i) for i in range(1,54)]
	for i in range(1,5):
		year_weeks.append((2021,i))
	select_posts = "SELECT * FROM submissions WHERE year == '{year}' and week == '{week}'"
	output_data = {}
	for year_week in tqdm(year_weeks):
		create_data(database,output_data,select_posts,year_week)
	with open("data/distribution/sentiment_"+database+".json","w") as outpuf:
		json.dump(output_data,outpuf)
save_data("ukpolitics")
save_data("nfl")
