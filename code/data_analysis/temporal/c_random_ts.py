import numpy as np
import sqlite3
import pandas as pd
import pytz
import json
from datetime import datetime
from tqdm import tqdm


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
    #get only TOP 100 by num comments
    df_posts = pd.DataFrame(posts)
    df_posts["num_comments"] = pd.to_numeric(df_posts["num_comments"])
    df_posts = df_posts.sort_values(by = ["num_comments"])
    df_posts = df_posts.tail(100)
    key = str(year_week[0])+"_"+str(year_week[1])
    output_data[key] = {}
    #comments
    select_comms = "SELECT * FROM comments WHERE id_submission = '{id_link}'"
    for _,post in df_posts.iterrows():
        c.execute(select_comms.format(id_link = post["id_submission"]))
        temp_ld = []
        temp_ld.append({
            "sentiment":1,
            "time": datetime.fromtimestamp(int(post["utc"]),tz = utc_tmzone),
            "utc":int(post["utc"])
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
                "sentiment":1,
                "time":datetime.fromtimestamp(int(comm["utc"]),tz = utc_tmzone),
                "utc":int(comm["utc"])
            })
        data_post = datetime.fromtimestamp(int(post["utc"]),tz = utc_tmzone).strftime("%d/%m/%Y")
        output_data[key][post["id_submission"]] = {}
        output_data[key][post["id_submission"]]["data"] = []
        output_data[key][post["id_submission"]]["date"] = data_post
        output_data[key][post["id_submission"]]["num_comments"] = int(post["num_comments"])
        #shuffle
        df = pd.DataFrame(temp_ld)
        df = df.sort_values(by = ["time"])
        for x in range(100):
            t_df = df
            utcs = t_df["utc"]
            t0 = t_df.iloc[0]["utc"]
            delta_ts = utcs.diff().dropna()
            random_perm_delta = np.random.permutation(delta_ts)
            sum_random_perm_delta = np.cumsum(random_perm_delta)
            new_utc = [t0]
            for x in sum_random_perm_delta:
                new_utc.append(t0+x)
            t_df["utc"] = new_utc
            t_df["time"] = t_df.apply(lambda x: datetime.fromtimestamp(x["utc"],tz = utc_tmzone),axis = 1)
            aggdf = t_df.groupby(pd.Grouper(freq = freq,key = 'time')).sentiment.sum().reset_index()
            sents = aggdf.sentiment.tolist()
            if len(sents) < max_number:
                for x in range(0,max_number-len(sents)):
                    sents.append(0.0)
            if len(sents) > max_number:
                sents = sents[:max_number]
            output_data[key][post["id_submission"]]["data"].append(sents)
    conn.close()


def create_trees(database):
    year_weeks = [(2020,i) for i in range(1,54)]
    for i in range(1,5):
        year_weeks.append((2021,i))
    select_posts = "SELECT * FROM submissions WHERE year == '{year}' and week == '{week}'"
    output_data = {}
    for year_week in tqdm(year_weeks):
        create_data(database,output_data,select_posts,year_week,"5min",24*12)
    with open("data/ts_interactions/interactions_random_"+database+".json","w") as outpuf:
        json.dump(output_data,outpuf)


create_trees("nba")
