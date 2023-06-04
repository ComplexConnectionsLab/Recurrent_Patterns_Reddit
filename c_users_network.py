import sqlite3
from tqdm import tqdm
import pandas as pd
import networkx as nx


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def create_user_network(year_week_tuple,kind):
    year = year_week_tuple[0]
    week = year_week_tuple[1]
    year_week = str(year)+"_"+str(week)
    conn = sqlite3.connect("data/{kind}.db".format(kind = kind))
    conn.row_factory = dict_factory
    c = conn.cursor()
    c.execute("SELECT author, count(*) as c FROM comments WHERE week == '{week}' AND year == '{year}' GROUP BY author HAVING c <= 5".format(week = week, year = year))
    remove_authors = [row["author"] for row in c]
    c2 = conn.cursor()
    c.execute("SELECT DISTINCT * FROM comments WHERE week == '{week}' AND year == '{year}'".format(week = week, year = year))
    output_data = []
    for row in c:
        if row["author"] in remove_authors:
            continue
        if row["author"].lower().endswith("bot"):
            continue
        if row["author"] == "AutoModerator":
            continue
        if row["author"] == "[deleted]":
            continue
        if row["id_parent"][:3] == "t1_":
            #comments
            c2.execute("SELECT author FROM comments WHERE id_comment == '{id_comment}'".format(id_comment = row["id_parent"]))
            results = c2.fetchall()
            if len(results) == 0:
                continue
            else:
                if results[0]["author"] in remove_authors:
                    continue
                if results[0]["author"].lower().endswith("bot"):
                    continue
                if results[0]["author"] == "[deleted]":
                    continue
                if results[0]["author"] in "AutoModerator":
                    continue
                output_data.append({"src":row["author"],"dst":results[0]["author"]})
        else:
            #posts
            c2.execute("SELECT author FROM submissions WHERE id_submission == '{id_submission}'".format(id_submission = row["id_parent"]))
            results = c2.fetchall()
            if len(results) == 0:
                continue
            else:
                if results[0]["author"] in remove_authors:
                    continue
                if results[0]["author"].lower().endswith("bot"):
                    continue
                if results[0]["author"] == "[deleted]":
                    continue
                if results[0]["author"] in "AutoModerator":
                    continue
                output_data.append({"src":row["author"],"dst":results[0]["author"]})
    df = pd.DataFrame(output_data)
    df.to_csv("data/network/network_user_{kind}_{year_week}.csv".format(kind = kind,year_week = year_week),sep = ";",index = False)
    conn.close()
    with open("data/network/network_user_{kind}_{year_week}.csv".format(kind = kind,year_week = year_week),"r") as inpuf:
        df = pd.read_csv(inpuf, sep = ";")
    graph = nx.DiGraph()
    for _,row in df.iterrows():
        src = row["src"]
        dst = row["dst"]
        if graph.has_edge(src,dst):
            graph.edges[(src,dst)]["weight"] += 1
        else:
            graph.add_edge(src,dst,weight = 1)
    nx.write_gpickle(graph,"data/network/network_user_{kind}_{year_week}.gpickle".format(kind = kind,year_week = year_week))


def main(kind):
    year_weeks = [(2020,i) for i in range(1,54)]
    for i in range(1,5):
        year_weeks.append((2021,i))
    for year_week in tqdm(year_weeks):
        create_user_network(year_week,kind)

main("politics")
