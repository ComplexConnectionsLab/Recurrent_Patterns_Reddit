import sqlite3
from itertools import combinations
from tqdm import tqdm
import pandas as pd
import networkx as nx
import numpy as np
import json
from datetime import datetime
import pytz
from datetime import datetime,timedelta
import json
import numpy as np


def change_name(row,ev,inwhat):
    if row == ev[0]:
        return inwhat
    else:
        return "Week Before"


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
            dt = np.mean(data[t][user]["dt"])/3600
            dr = data[t][user]["w2v"]
            xs.append({"time":time,"yw":t,"m":dr,"dt":dt,"user":user})
    df = pd.DataFrame(xs)
    return df


def main(kind,event_chosen):
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
        #March 11 – COVID-19 pandemic: The World Health Organization declares the COVID-19 outbreak a pandemic.[51]
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
        dict_events[k] = [str(year)+"_"+str(week)]
        v_1 = v-timedelta(days = 7)
        year = v_1.year
        week = v_1.isocalendar()[1]
        if str(year)+"_"+str(week) == "2021_53":
            dict_events[k].append("2020_53")
        else:
            dict_events[k].append(str(year)+"_"+str(week))
    #def main
    df = get_user_w2v(kind)
    df = df.sort_values(by = ["time"])
    ev = dict_events[event_chosen]
    N = 4
    df["dt_category"] = pd.qcut(df["dt"], N, labels=[str(i) for i in range(N)])
    df = df[df["yw"].isin(ev)]
    df["yw_name"] = df.apply(lambda x:change_name(x["yw"],ev,event_chosen),axis = 1)
    year_weeks = df["yw"].unique().tolist()
    #output_data
    for year_week in year_weeks:
        tdf = df[df["yw"] == year_week]
        yname = tdf["yw_name"].unique().tolist()[0]
        graph = nx.read_gpickle("data/network/network_user_filter_{kind}_{year_week}.gpickle".format(kind = kind,year_week = year_week))
        graph = graph.copy()
        nodes = list(graph.nodes())
        users = tdf["user"].tolist()
        node_to_remove = list(set(nodes)-set(users))
        graph.remove_nodes_from(node_to_remove)
        dict_user_value = {row["user"]:row["dt"] for _,row in tdf.iterrows()}
        for node in graph.nodes():
            graph.nodes[node]["dt"] = dict_user_value[node]
        nx.write_gexf(graph,"data/network/toplot/network_user_filter_{kind}_{year_week}.gexf".format(kind = kind,year_week = yname))


main("nba","NBA Trades")
main("politics","US 2020")
main("nfl","NFL Kickoff Game")
