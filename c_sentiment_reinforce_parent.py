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
    posts = df_posts["id_submission"].tolist()
    select_comments = "SELECT * FROM comments WHERE year == '{year}' and week == '{week}'"
    c.execute(select_comments.format(year = str(year_week[0]), week = str(year_week[1])))
    key = str(year_week[0])+"_"+str(year_week[1])
    output_data[key] = []
    #comments
    select_comms = "SELECT * FROM comments WHERE id_comment == '{id_link}'"
    select_posts = "SELECT * FROM submissions WHERE id_submission =='{id_link}'"
    c2 = conn.cursor()
    for row in c:
        if row["text"] == "[removed]":
            continue
        if row["id_submission"] not in posts:
            continue
        if row["author"].lower().endswith("bot"):
            continue
        if row["author"] == "AutoModerator":
            continue
        children_sentiment = sia.polarity_scores(row["text"].lower())["compound"]
        if row["id_parent"][:2] == "t3":
            #post
            c2.execute(select_posts.format(id_link = row["id_parent"]))
            for res in c2:
                dt = int(row["utc"]) - int(res["utc"])
                if dt > 86400:
                    continue
                parent_sentiment = sia.polarity_scores(res["title"].lower() + res["text"].lower())["compound"]
        elif row["id_parent"][:2] == "t1":
            #comments
            c2.execute(select_comms.format(id_link = row["id_parent"]))
            for res in c2:
                dt = int(row["utc"]) - int(res["utc"])
                if dt > 86400:
                    continue
                parent_sentiment = sia.polarity_scores(res["text"].lower())["compound"]
        output_data[key].append((children_sentiment,parent_sentiment))
    conn.close()


def save_data(database):
    year_weeks = [(2020,i) for i in range(1,54)]
    for i in range(1,5):
        year_weeks.append((2021,i))
    select_posts = "SELECT * FROM submissions WHERE year == '{year}' and week == '{week}'"
    output_data = {}
    for year_week in tqdm(year_weeks):
        create_data(database,output_data,select_posts,year_week)
    with open("data/distribution/reinforce_sentiment_"+database+".json","w") as outpuf:
        json.dump(output_data,outpuf)


save_data("europe")
