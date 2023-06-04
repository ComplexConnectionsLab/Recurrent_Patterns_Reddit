import sqlite3
import pandas as pd
import numpy as np
import json
import re
import string
from tqdm import tqdm
from datetime import datetime
def create_data(database):
	#sqlite
	def dict_factory(cursor, row):
		d = {}
		for idx, col in enumerate(cursor.description):
			d[col[0]] = row[idx]
		return d
	conn = sqlite3.connect("./data/"+database+".db")
	conn.row_factory = dict_factory
	c = conn.cursor()
	#get weeks
	c.execute('SELECT DISTINCT year || "_" || week as ddd FROM comments')
	weeks = [row["ddd"] for row in c]
	#get users
	c.execute('SELECT author, week, year || "_" || week as year_week, count(*) as c FROM comments GROUP BY author, year_week HAVING c > 5')
	tmp_week_users = {}
	for row in c:
		if row["author"].lower().endswith("bot"):
			continue
		if row["author"] == "AutoModerator":
			continue
		if row["author"] == "[deleted]":
			continue
		key = (row["year_week"].split("_")[0],row["year_week"].split("_")[1])
		if key not in tmp_week_users:
			tmp_week_users[key] = []
		tmp_week_users[key].append(row["author"])
	dict_week_users = {k:list(set(v)) for (k,v) in tmp_week_users.items()}
	select_comms = "SELECT * FROM comments WHERE author == '{author}' AND week == '{week}' AND year == '{year}'"
	select_parent_comm = "SELECT count(*) as c FROM comments WHERE id_parent == '{id_parent}'"
	c2 = conn.cursor()
	#get data
	output_data = {}
	for (week_year,users) in tqdm(dict_week_users.items(),total = len(dict_week_users.keys())):
		year = week_year[0]
		week = week_year[1]
		year_week = week_year[0]+"_"+week_year[1]
		output_data[year_week] = [[],[]]
		#for each users
		for user in users:
			c.execute(select_comms.format(author = user,year = year,week = week))
			out_degree = 0
			in_degree = 0
			for comm in c:
				id_comment = comm["id_comment"]
				c2.execute(select_parent_comm.format(id_parent = id_comment))
				in_degree += list(c2.fetchall())[0]["c"]
				#parent is a comment ?
				if comm["id_parent"][:3] == "t1_":
					out_degree+=1
			output_data[year_week][0].append(out_degree)
			output_data[year_week][1].append(in_degree)
	conn.close()
	with open("data/users/users_degree_"+database+".json","w") as outpuf:
		json.dump(output_data,outpuf)
create_data("cryptocurrency")
create_data("wsb")
