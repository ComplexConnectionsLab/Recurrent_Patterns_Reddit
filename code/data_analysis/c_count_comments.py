import sqlite3
import pandas as pd
from tqdm import tqdm


def create_data(database,year_week,total0,x0,y0):
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
    select_posts = "SELECT * FROM submissions WHERE year == '{year}' and week == '{week}'"
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
    #get total first
    select_comms = "SELECT count(*) as c FROM comments WHERE year == '{year}' and week == '{week}'"
    c.execute(select_comms.format(year=year_week[0], week=year_week[1]))
    total = list(c.fetchall())[0]["c"]
    x = 0
    y = 0
    #comments
    select_comms = "SELECT * FROM comments WHERE id_submission = '{id_link}'"
    for _,post in df_posts.iterrows():
        c.execute(select_comms.format(id_link = post["id_submission"]))
        for comm in c:
            if comm["text"] == "[removed]":
                continue
            if post["author"].lower().endswith("bot"):
                continue
            if post["author"] == "AutoModerator":
                continue
            dt = int(comm["utc"]) - int(post["utc"])
            y += 1
            if dt > 86400:
                continue
            x += 1
    total0 += total
    x0 += x
    y0 += y
    conn.close()
    return total0, x0, y0


def get_data():
    output_data = []
    for database in ["nba","nfl","europe","politics"]:
        year_weeks = [(2020,i) for i in range(1,54)]
        for i in range(1,5):
            year_weeks.append((2021,i))
        x0 = 0
        total0 = 0
        y0 = 0
        for year_week in tqdm(year_weeks):
            total0, x0, y0 = create_data(database,year_week,total0,x0,y0)
        output_data.append({"kind":database,"total0":total0,"x0":x0,"y0":y0,"r":x0/total0,"f":x0/y0})
    df = pd.DataFrame(output_data)
    print(df)


get_data()