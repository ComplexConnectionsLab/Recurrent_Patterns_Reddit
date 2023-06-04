import pytz
import json
from datetime import datetime
import os
import pandas as pd
from tqdm import tqdm
def create_posts(kind):
	est = pytz.timezone('US/Eastern')
	utc_tmzone = pytz.utc
	data = [f for f in os.listdir("data_raw/"+kind+"/posts/") if f.endswith(".json")]
	output_data = []
	for datum in tqdm(data):
		with open("data_raw/"+kind+"/posts/"+datum,"r") as inpuf:
			submissions = json.load(inpuf)
		for submission in submissions:
			if submission['author'] == '[deleted]':
				author = "[deleted]"
				author_id = "deleted"
			else:
				author = submission["author"]
				author_id = submission["author_fullname"]
			subscribers = submission["subreddit_subscribers"]
			utc = submission["created_utc"]
			score = submission["score"]
			comments = submission["num_comments"]
			id_sub = "t3_"+submission["id"]
			if submission["selftext"] == "[removed]":
				text = ""
			else:
				text = submission["selftext"]
			title = submission["title"]
			day_dt = datetime.fromtimestamp(int(utc),tz = utc_tmzone)
			year = day_dt.year
			month = day_dt.month
			day = day_dt.day
			week = day_dt.isocalendar()[1]
			output_data.append({
							"author":author,
							"author_id":author_id,
							"utc":utc,
							"score":score,
							"num_comments":comments,
							"id_submission":id_sub,
							"text":text,
							"title":title,
							"subscribers":subscribers,
							"day":day,
							"month":month,
							"year":year,
							"week":week
							})
	df = pd.DataFrame(output_data)
	df = df.sort_values(by = ["utc"])
	df.to_csv("data/"+kind+"_posts.csv",sep = ";",index = False)

def unify_comments(kind):
	output_data = []
	est = pytz.timezone('US/Eastern')
	utc_tmzone = pytz.utc
	for x in range(1,4):
		with open("data/"+kind+"_comments_"+str(x)+".csv","r") as inpuf:
			df = pd.read_csv(inpuf, sep = ";",dtype = "object")
		for _,row in df.iterrows():
			try:
				day_dt = datetime.fromtimestamp(int(row["utc"]),tz = utc_tmzone)
				year = day_dt.year
				month = day_dt.month
				day = day_dt.day
				week = day_dt.isocalendar()[1]
				output_data.append({
									"author":row["author"],
									"author_id":row["author_id"],
									"utc":row["utc"],
									"score":row["score"],
									"id_comment":row["id_comment"],
									"id_submission":row["id_submission"],
									"id_parent":row["id_parent"],
									"text":row["text"],
									"day":day,
									"month":month,
									"year":year,
									"week":week
									})
			except:
				print(row)
				print(kind)
	df = pd.DataFrame(output_data)
	df = df.sort_values(by = ["utc"])
	df.to_csv("data/"+kind+"_comments.csv",sep = ";",index = False)


def create_comments(kind):
	#comments
	data = [f for f in os.listdir("data_raw/"+kind+"/comments/") if f.endswith(".json")]
	output_data = []
	for datum in tqdm(data):
		with open("data_raw/"+kind+"/comments/"+datum,"r") as inpuf:
			comments = json.load(inpuf)
		for comment in comments:
			if comment['author'] == '[deleted]':
				author = "[deleted]"
				author_id = "deleted"
			else:
				author = comment["author"]
				author_id = comment["author_fullname"]
			body = comment["body"]
			utc = comment["created_utc"]
			score = comment["score"]
			id_sub = comment["link_id"]
			id_comment = "t1_" + comment["id"]
			id_parent = comment["parent_id"]
			output_data.append({
							"author":author,
							"author_id":author_id,
							"utc":utc,
							"score":score,
							"id_comment":id_comment,
							"id_submission":id_sub,
							"id_parent":id_parent,
							"text":body
							})
	df = pd.DataFrame(output_data)
	df.to_csv("data/"+kind+"_comments_3.csv",sep = ";",index = False)


create_posts("cryptocurrency")
create_posts("europe")
create_posts("nba")
create_posts("politics")
create_posts("science")
create_posts("soccer")
create_posts("sports")
create_posts("stocks")
