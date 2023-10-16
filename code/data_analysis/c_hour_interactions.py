import sqlite3
import pandas as pd
import pytz
import json
from datetime import datetime
from tqdm import tqdm
def create_data(database,output_data,year_week):
    if database == "europe":
        tzinfo = pytz.timezone("Europe/Amsterdam")
    else:
        tzinfo = pytz.timezone('US/Eastern')
    #sqlite
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
    tmp_data = {}
    #post
    conn = sqlite3.connect("./data/"+database+".db")
    conn.row_factory = dict_factory
    c = conn.cursor()
    select_posts = "SELECT * FROM submissions WHERE year == '{year}' and week == '{week}'"
    c.execute(select_posts.format(year = str(year_week[0]), week = str(year_week[1])))
    for post in c:
        if post["text"] == "[removed]":
            continue
        if post["author"].lower().endswith("bot"):
            continue
        if post["author"] == "AutoModerator":
            continue
        day_time = datetime.fromtimestamp(int(post["utc"]),tz = tzinfo)
        hour = day_time.hour
        if hour not in tmp_data:
            tmp_data[hour] = 0
        tmp_data[hour] += 1
    #comments
    select_comments = "SELECT * FROM comments WHERE year == '{year}' and week == '{week}'"
    c.execute(select_comments.format(year = str(year_week[0]), week = str(year_week[1])))
    for row in c:
        if row["author"].lower().endswith("bot"):
            continue
        if row["author"] == "AutoModerator":
            continue
        day_time = datetime.fromtimestamp(int(row["utc"]),tz = tzinfo)
        hour = day_time.hour
        if hour not in tmp_data:
            tmp_data[hour] = 0
        tmp_data[hour] += 1
    key = str(year_week[0])+"_"+str(year_week[1])
    output_data[key] = tmp_data
    conn.close()


def save_data(database):
    year_weeks = [(2020,i) for i in range(1,54)]
    for i in range(1,5):
        year_weeks.append((2021,i))
    output_data = {}
    for year_week in tqdm(year_weeks):
        create_data(database,output_data,year_week)
    with open("data/distribution/hour_interactions_"+database+".json","w") as outpuf:
        json.dump(output_data,outpuf)


save_data("europe")
save_data("politics")
save_data("nba")
save_data("nfl")