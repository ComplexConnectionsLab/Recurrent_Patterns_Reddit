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
from scipy import linalg


def get_omega(graph):
    L = nx.laplacian_matrix(graph)
    omega = linalg.pinv(L.todense())
    return omega


def get_resistance_distance(omega,i,j):
    return omega[i,i]+omega[j,j]-omega[i,j]-omega[j,i]


def change_name(row,ev,inwhat):
    if row == ev[0]:
        return inwhat
    else:
        return "Week Before"


def get_users(kind):
    year_weeks = ["2020_"+str(i) for i in range(1,54)]
    for i in range(1,5):
        year_weeks.append("2021_"+str(i))
    with open("data/users/users_compression_"+kind+"_all.json","r") as inpuf:
        data_compression = json.load(inpuf)
    xs = []
    for i in range(0,len(year_weeks)):
        t = year_weeks[i]
        users = list(data_compression[t].keys())
        time = datetime.strptime(t + '-1', "%Y_%W-%w")
        for user in users:
            compression = data_compression[t][user]
            xs.append({"time":time,"yw":t,"user":user,"compression":compression})
    df = pd.DataFrame(xs)
    return df

def main(kind):
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
    dict_week_before = {}
    for (k,v) in tmp.items():
        v.replace(tzinfo = utc_tmzone)
        year = v.year
        week = v.isocalendar()[1]
        dict_events[k] = str(year)+"_"+str(week)
        v_1 = v-timedelta(days = 7)
        year = v_1.year
        week = v_1.isocalendar()[1]
        if str(year)+"_"+str(week) == "2021_53":
            dict_week_before[k] = "2020_53"
        else:
            dict_week_before[k] = str(year)+"_"+str(week)
    dict_reddit_events = {
                            "europe":["Brexit","Cyprus","Belarus Protest","Lockdown Ease","US 2020","Capitol Hill","Coronavirus"],
                            "politics":["Trump","Trump Covid","US 2020","Capitol Hill","Coronavirus","BLM"],
                            "nba":["Kobe Bryant","NBA Stop","NBA Restart","Orlando","NBA Finals","NBA Trades"],
                            "nfl":["NFL Draft","NFL Kickoff Game","SuperBowl LIV","NFL Trades","NFL PlayOff"]
                        }
    year_weeks = [str(2020) + "_"+str(i) for i in range(1,54)]
    for i in range(1,5):
        year_weeks.append(str(2021) + "_" + str(i))
    yws = []
    flags = []
    for ev in dict_reddit_events[kind]:
        week = dict_events[ev]
        week_before = dict_week_before[ev]
        yws.append({"year_week": week,"event":ev,"is_event":"Yes"})
        yws.append({"year_week": week_before,"event":ev,"is_event":"Week Before"})
        flags.append(week)
        flags.append(week_before)
    for year_week in year_weeks:
        if year_week in flags:
            continue
        yws.append({"year_week": year_week,"event":"No Event","is_event":"No"})
    ev_df = pd.DataFrame(yws)
    users_df = get_users(kind)
    df = users_df.sort_values(by = ["time"])
    output_data = []
    for year_week in tqdm(year_weeks):
        info_week = ev_df[ev_df["year_week"] == year_week].iloc[0]
        info_week = {c:info_week[c] for c in ["year_week","event","is_event"]}
        tdf = df[df["yw"] == year_week]
        graph = nx.read_gpickle("data/network/network_user_{kind}_{year_week}.gpickle".format(kind = kind,year_week = year_week))
        #omega = get_omega(graph)
        nodes = list(graph.nodes())
        users = tdf["user"].tolist()
        dict_user_value = {row["user"]:row["compression"] for _,row in tdf.iterrows()}
        for user in users:
            total = 0.0
            v = 0.0
            if user not in nodes:
                continue
            for neighbor in graph.neighbors(user):
                if neighbor in dict_user_value:
                    v+=dict_user_value[neighbor]
                    total+=1
            if total == 0:
                continue
            value_user = dict_user_value[user]
            value_neighbors = v/total
            output_data.append({"year_week":year_week,"user":user,"value_user":value_user,"value_neighbors":value_neighbors,"event":info_week["event"],"is_event":info_week["is_event"]})
    df = pd.DataFrame(output_data)
    df.to_csv("data/to_plot/semantic_paradox_{kind}.csv".format(kind=kind),sep = ",",index = False)


main("nba")
main("politics")
main("nfl")
main("europe")