import sqlite3
import pandas as pd
import pytz
from datetime import datetime,timedelta
from tqdm import tqdm
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.dates as mdates
matplotlib.style.use("ggplot")

def get_first_user(database):
	def dict_factory(cursor, row):
		d = {}
		for idx, col in enumerate(cursor.description):
			d[col[0]] = row[idx]
		return d
	conn = sqlite3.connect("./data/"+database+".db")
	conn.row_factory = dict_factory
	c = conn.cursor()
	c.execute('SELECT author, author_id, min(cast(utc as int)) as mu, year || "_" || month || "_" || day as ddd FROM submissions WHERE author != "[deleted]" GROUP BY author_id')
	output = [{"author_id":p["author_id"],"date":p["ddd"]} for p in c]
	c.execute('SELECT author, author_id, min(cast(utc as int)) as mu, year || "_" || month || "_" || day as ddd FROM comments WHERE author != "[deleted]" GROUP BY author_id')
	output.extend([{"author_id":p["author_id"],"date":p["ddd"]} for p in c])
	df = pd.DataFrame(output)
	gdf = df.groupby(by = ["author_id"],as_index = False).date.min()
	tdf = gdf.groupby(by = ["date"],as_index = False).count().reset_index()
	tdf = tdf.rename(columns = {"author_id":"fist_time_users"})
	conn.close()
	return tdf

def get_last_user(database):
	def dict_factory(cursor, row):
		d = {}
		for idx, col in enumerate(cursor.description):
			d[col[0]] = row[idx]
		return d
	conn = sqlite3.connect("./data/"+database+".db")
	conn.row_factory = dict_factory
	c = conn.cursor()
	c.execute('SELECT author, author_id, max(cast(utc as int)) as mu, year || "_" || month || "_" || day as ddd FROM submissions WHERE author != "[deleted]" GROUP BY author_id')
	output = [{"author_id":p["author_id"],"date":p["ddd"]} for p in c]
	c.execute('SELECT author, author_id, max(cast(utc as int)) as mu, year || "_" || month || "_" || day as ddd FROM comments WHERE author != "[deleted]" GROUP BY author_id')
	output.extend([{"author_id":p["author_id"],"date":p["ddd"]} for p in c])
	df = pd.DataFrame(output)
	gdf = df.groupby(by = ["author_id"],as_index = False).date.max()
	tdf = gdf.groupby(by = ["date"],as_index = False).count().reset_index()
	tdf = tdf.rename(columns = {"author_id":"last_time_users"})
	conn.close()
	return tdf

def get_data_activity(database):
	#sqlite
	def dict_factory(cursor, row):
		d = {}
		for idx, col in enumerate(cursor.description):
			d[col[0]] = row[idx]
		return d
	conn = sqlite3.connect("./data/"+database+".db")
	conn.row_factory = dict_factory
	c = conn.cursor()
	c.execute('SELECT count(*) as c, year || "_" || month || "_" || day as ddd, author_id, author FROM comments GROUP BY ddd,author_id order by author_id')
	comments = [{"comments_per_author":row["c"],"date":row["ddd"],"author":row["author_id"]} for row in c if not row["author"].endswith("bot") or row["author"] == "AutoModerator"]
	c.execute('SELECT count(*) as c, year || "_" || month || "_" || day as ddd, author_id, author FROM submissions GROUP BY ddd,author_id order by author_id')
	posts = [{"posts_per_author":row["c"],"date":row["ddd"],"author":row["author_id"]} for row in c if not row["author"].endswith("bot") or row["author"] == "AutoModerator"]
	conn.close()
	df_posts = pd.DataFrame(posts)
	df_comments = pd.DataFrame(comments)
	df_posts = df_posts[df_posts["author"] != "deleted"]
	df_comments = df_comments[df_comments["author"] != "deleted"]
	return df_posts, df_comments

def get_post_comments(database):
	#sqlite
	def dict_factory(cursor, row):
		d = {}
		for idx, col in enumerate(cursor.description):
			d[col[0]] = row[idx]
		return d
	conn = sqlite3.connect("./data/"+database+".db")
	conn.row_factory = dict_factory
	c = conn.cursor()
	c.execute('SELECT count(*) as c, year || "_" || month || "_" || day as ddd FROM submissions GROUP BY ddd')
	posts = [{"posts":row["c"],"date":row["ddd"]} for row in c]
	c.execute('SELECT count(*) as c, year || "_" || month || "_" || day as ddd FROM comments GROUP BY ddd')
	comments = [{"comments":row["c"],"date":row["ddd"]} for row in c]
	conn.close()
	df_posts = pd.DataFrame(posts)
	df_comments = pd.DataFrame(comments)
	return df_posts, df_comments

def get_data_leaves(database):
	output_data_leave = []
	def dict_factory(cursor, row):
		d = {}
		for idx, col in enumerate(cursor.description):
			d[col[0]] = row[idx]
		return d
	conn = sqlite3.connect("./data/"+database+".db")
	conn.row_factory = dict_factory
	c = conn.cursor()
	c.execute('SELECT id_submission, utc, year || "_" || month || "_" || day as ddd FROM submissions')
	posts = [row for row in c]
	c2 = conn.cursor()
	select_comms = "SELECT * FROM comments WHERE id_submission = '{id_link}'"
	select_parent_comm = "SELECT * FROM comments WHERE id_parent = '{id_comment}'"
	for post in posts:
		c.execute(select_comms.format(id_link = post["id_submission"]))
		for comm in c:
			dt = int(comm["utc"]) - int(post["utc"])
			c2.execute(select_parent_comm.format(id_comment = comm["id_comment"]))
			result_query = list(c2.fetchall())
			if len(result_query) == 0:
				output_data_leave.append({
								"leaves":1,
								"date": post["ddd"]
								})
	conn.close()
	df = pd.DataFrame(output_data_leave)
	aggdf = df.groupby(by = ["date"],as_index = False).leaves.sum().reset_index()
	return aggdf

def save_data_activity(database):
	posts_per_author, comments_per_author = get_data_activity(database)
	posts_per_author.to_csv("data/basic_stats/"+database+"_ppa.csv",index = False, sep = ";")
	comments_per_author.to_csv("data/basic_stats/"+database+"_cpa.csv",index = False, sep = ";")

def save_data(database):
	first_user = get_first_user(database)
	last_user = get_last_user(database)
	posts, comments = get_post_comments(database)
	leaves =  get_data_leaves(database)
	df_pc = pd.merge(posts,comments, how = "inner",on = "date")
	df_users = pd.merge(first_user,last_user, how = "inner",on = "date")
	df_leaves = pd.merge(df_pc,leaves,how = "inner",on = "date")
	df = pd.merge(df_leaves,df_users, how = "inner",on = "date")
	with open("data/basic_stats/"+database+"_ppa.csv","r") as inpuf:
		df_ppa = pd.read_csv(inpuf,sep = ";")
	with open("data/basic_stats/"+database+"_cpa.csv","r") as inpuf:
		df_cpa = pd.read_csv(inpuf,sep = ";")
	gdf_ppa = df_ppa.groupby(by =["date"]).posts_per_author.mean().reset_index()
	gdf_cpa = df_cpa.groupby(by =["date"]).comments_per_author.mean().reset_index()
	df_pa = pd.merge(gdf_cpa,gdf_ppa,how = "inner",on = "date")
	fdf = pd.merge(df,df_pa,how = "inner",on = "date")
	del fdf["index"]
	del fdf["index_x"]
	del fdf["index_y"]
	fdf.to_csv("data/basic_stats/"+database+".csv",index = False, sep = ";")
save_data_activity("nfl")
save_data("nfl")
save_data_activity("ukpolitics")
save_data("ukpolitics")
