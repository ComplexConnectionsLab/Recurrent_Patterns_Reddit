import sqlite3
import pandas as pd
import numpy as np
import json
import pytz
from datetime import datetime
import networkx as nx


def get_user_w2v(kind):
    year_weeks = ["2020_"+str(i) for i in range(1,54)]
    for i in range(1,5):
        year_weeks.append("2021_"+str(i))
    with open("data/users/users_gyration_w2v_"+kind+".json","r") as inpuf:
        data = json.load(inpuf)
    xs = []
    for i in range(0,len(year_weeks)):
        t = year_weeks[i]
        users = list(data[t].keys())
        time = datetime.strptime(t + '-1', "%Y_%W-%w")
        for user in users:
            dts = np.array(data[t][user]["dt"])/3600
            dt = np.mean(dts)
            ats = np.array(data[t][user]["activation_time"])
            ats = np.sort(ats)
            dats = np.diff(ats)/3600
            at = np.mean(dats)
            dr = data[t][user]["w2v"]
            s = np.array(data[t][user]["excitement"])
            mask = s != 0.0
            s = s[mask]
            excitement = np.mean(s)
            xs.append({"time":time,"yw":t,"m":dr,"dt":dt,"at":at,"user":user,"excitement":excitement})
    df = pd.DataFrame(xs)
    return df


def create_data(database,select_posts,year_week,tdf):
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
    #comments
    select_comms = "SELECT * FROM comments WHERE id_submission = '{id_link}' ORDER BY cast(utc as INT) ASC"
    dict_users_posts = {}
    #
    graph = nx.read_gpickle("data/network/network_user_{kind}_{year_week}.gpickle".format(kind = database,year_week = key))
    nodes = list(graph.nodes())
    for _,post in df_posts.iterrows():
        c.execute(select_comms.format(id_link = post["id_submission"]))
        dict_users_posts[post["id_submission"]] = []
        if post["author"] in nodes:
            dict_users_posts[post["id_submission"]].append(post["author"])
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
            if comm["author"] in nodes:
                dict_users_posts[post["id_submission"]].append(comm["author"])
    conn.close()
    #
    dict_user_value = {row["user"]:[row["m"],row["at"]] for _,row in tdf.iterrows()}
    dict_output_post = {}
    for (post,users_to_clean) in dict_users_posts.items():
        users_posts = set(users_to_clean)
        dict_output_post[post] = [dict_user_value[user] for user in users_posts if user in dict_user_value]
    return dict_output_post


def save_data(database,event_chosen):
    #nlp
    df = get_user_w2v(database)
    #events
    if database == "europe":
        event_chosen_string = "e"+event_chosen.replace(" ", "_").lower()
    else:
        event_chosen_string = event_chosen.replace(" ", "_").lower()
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
        "NFL PlayOff 2020":datetime(2020,1,5),
        "SuperBowl LIV":datetime(2020,2,2),
        "NFL Trades":datetime(2020,3,18),
        "NFL PlayOff":datetime(2021,1,10),
    }
    dict_events = {}
    for (k,v) in tmp.items():
        v.replace(tzinfo = utc_tmzone)
        year = v.year
        week = v.isocalendar()[1]
        dict_events[k] = str(year)+"_"+str(week)
    ev = dict_events[event_chosen]
    tdf = df[df["yw"] == ev]
    #
    year_weeks = {"2020_{i}".format(i = i):(2020,i) for i in range(1,54)}
    for i in range(1,5):
        year_weeks["2021_{i}".format(i = i)]= (2021,i)
    year_week = year_weeks[ev]
    select_posts = "SELECT * FROM submissions WHERE year == '{year}' and week == '{week}'"
    output_data = create_data(database,select_posts,year_week,tdf)
    with open("data/w2v_posts/w2v_users_posts_"+event_chosen_string+".json","w") as outpuf:
        json.dump(output_data,outpuf)


save_data("nba","NBA Trades")
save_data("nba","NBA Restart")
save_data("nba","Orlando")
save_data("politics","US 2020")
save_data("politics","Capitol Hill")
save_data("politics","Trump")
save_data("nfl","NFL Kickoff Game")
save_data("nfl","SuperBowl LIV")
save_data("nfl","NFL Draft")
save_data("europe","US 2020")
save_data("europe","Capitol Hill")
save_data("europe","Brexit")