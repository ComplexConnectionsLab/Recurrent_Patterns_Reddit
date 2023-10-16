import sqlite3
import pandas as pd
import json
from tqdm import tqdm
from lempel_ziv_complexity import lempel_ziv_complexity


def create_data(database,output_data,select_posts,year_week,fdata):
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
	output_data[key] = {}
	fdata[key] = {}
	#comments
	select_comms = "SELECT * FROM comments WHERE id_submission = '{id_link}' ORDER BY cast(utc as INT) ASC"
	for _,post in df_posts.iterrows():
		c.execute(select_comms.format(id_link = post["id_submission"]))
		temp_string = post["title"].lower() + post["text"].lower()
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
			temp_string += comm["text"].lower()
		output_data[key][post["id_submission"]] = lempel_ziv_complexity(temp_string)/(len(temp_string))
		fdata[key][post["id_submission"]] = [lempel_ziv_complexity(temp_string),len(temp_string)]
	conn.close()


def save_data(database):
	year_weeks = [(2020,i) for i in range(1,54)]
	for i in range(1,5):
		year_weeks.append((2021,i))
	select_posts = "SELECT * FROM submissions WHERE year == '{year}' and week == '{week}'"
	output_data = {}
	fdata = {}
	for year_week in tqdm(year_weeks):
		create_data(database,output_data,select_posts,year_week,fdata)
	with open("data/ts_interactions/compression_"+database+".json","w") as outpuf:
		json.dump(output_data,outpuf)
	with open("data/ts_interactions/compression_check_"+database+".json","w") as outpuf:
		json.dump(fdata,outpuf)


save_data("politics")
save_data("nba")
save_data("nfl")
save_data("europe")