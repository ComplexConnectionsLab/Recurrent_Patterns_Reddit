import sqlite3
import pandas as pd
import numpy as np
import json
import re
import string
from tqdm import tqdm
from datetime import datetime


def create_data(database,output_data,select_posts,year_week):
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
    c2 = conn.cursor()
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
    #comments
    select_comms = "SELECT * FROM comments WHERE id_submission = '{id_link}' ORDER BY cast(utc as INT) ASC"
    select_comms2 = "SELECT * FROM comments WHERE id_comment == '{id_link}'"
    for _,post in df_posts.iterrows():
        c.execute(select_comms.format(id_link = post["id_submission"]))
        array_dist_to_post = []
        array_dist_to_parent = []
        for comm in c:
            if comm["text"] == "[removed]":
                continue
            if comm["author"].lower().endswith("bot"):
                continue
            if comm["author"] == "AutoModerator":
                continue
            dt = int(comm["utc"]) - int(post["utc"])
            if dt > 86400:
                continue
            array_dist_to_post.append(dt/3600)
            if comm["id_parent"][:2] == "t3":
                array_dist_to_parent.append(dt/3600)
            else:
                c2.execute(select_comms2.format(id_link = comm["id_parent"]))
                for res in c2:
                    dt = int(comm["utc"]) - int(res["utc"])
                    if dt > 86400:
                        continue
                    array_dist_to_parent.append(dt/3600)
        #
        output_data[key][post["id_submission"]] = [array_dist_to_parent,array_dist_to_post]
    conn.close()


def save_data(database):
    #
    year_weeks = [(2020,i) for i in range(1,54)]
    for i in range(1,5):
        year_weeks.append((2021,i))
    select_posts = "SELECT * FROM submissions WHERE year == '{year}' and week == '{week}'"
    output_data = {}
    for year_week in tqdm(year_weeks):
        create_data(database,output_data,select_posts,year_week)
    with open("data/time_posts/posts_time_"+database+".json","w") as outpuf:
        json.dump(output_data,outpuf)


save_data("politics")
save_data("nba")
save_data("nfl")
save_data("europe")
