import sqlite3
import pandas as pd
import json
import re
import string
from tqdm import tqdm
from datetime import datetime
#nlp
from lempel_ziv_complexity import lempel_ziv_complexity

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
    #get users
    c.execute('SELECT author, week, ddd, count(*) as c FROM (SELECT author, author_id, week, year || "_" || week as ddd FROM submissions UNION ALL SELECT author, author_id, week, year || "_" || week as ddd FROM comments) GROUP BY author, ddd HAVING c > 5')
    tmp_week_users = {}
    wu_df = []
    for row in c:
        if row["author"].lower().endswith("bot"):
            continue
        if row["author"] == "AutoModerator":
            continue
        if row["author"] == "[deleted]":
            continue
        key = (row["ddd"].split("_")[0],row["ddd"].split("_")[1])
        if key not in tmp_week_users:
            tmp_week_users[key] = []
        tmp_week_users[key].append(row["author"])
        wu_df.append({"yw":key,"user":row["author"]})
    df = pd.DataFrame(wu_df)
    x = len(tmp_week_users.keys())
    gdf = df.groupby(by = ["user"]).count().reset_index()
    gdf["yw"] = gdf["yw"]/x
    gdf = gdf.sort_values(by = ["yw"],ascending = False)
    gdf = gdf[gdf["yw"]>0.5]
    users_to_mantain = set(gdf["user"].tolist())
    dict_week_users = {k:list(set(v).intersection(users_to_mantain)) for (k,v) in tmp_week_users.items()}
    select_posts = "SELECT * FROM submissions WHERE author == '{author}' AND week == '{week}' AND year == '{year}'"
    select_comms = "SELECT * FROM comments WHERE author == '{author}' AND week == '{week}' AND year == '{year}'"
    #get week
    output_data = {}
    for (week_year,users) in tqdm(dict_week_users.items(),total = len(dict_week_users.keys())):
        year = week_year[0]
        week = week_year[1]
        year_week = week_year[0]+"_"+week_year[1]
        output_data[year_week] = {}
        for user in users:
            temp_string = ""
            #posts
            c.execute(select_posts.format(author = user,year = year,week = week))
            for row in c:
                if row["text"] == "[removed]":
                    temp_string += ""
                else:
                    temp_string += row["title"].lower() + row["text"].lower()
            #comments
            c.execute(select_comms.format(author = user,year = year,week = week))
            for row in c:
                if row["text"] == "[removed]":
                    temp_string += ""
                else:
                    temp_string += row["text"].lower()
            #gran final'
            output_data[year_week][user] = lempel_ziv_complexity(temp_string)/(len(temp_string))
    conn.close()
    with open("data/users/users_compression_"+database+".json","w") as outpuf:
        json.dump(output_data,outpuf)


create_data("nba")
create_data("nfl")
create_data("politics")
create_data("europe")
