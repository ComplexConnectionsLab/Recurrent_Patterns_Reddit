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


def get_user_w2v(kind):
    year_weeks = ["2020_"+str(i) for i in range(1,54)]
    for i in range(1,5):
        year_weeks.append("2021_"+str(i))
    with open("data/distribution/sentiment_"+kind+".json","r") as inpuf:
        data_sentiment = json.load(inpuf)
    with open("data/users/users_gyration_w2v_"+kind+".json","r") as inpuf:
        data = json.load(inpuf)
    with open("data/users/users_compression_"+kind+".json","r") as inpuf:
        data_compression = json.load(inpuf)
    xs = []
    for i in range(0,len(year_weeks)):
        t = year_weeks[i]
        users = list(data[t].keys())
        ds = np.array(data_sentiment[t])
        mask = ds != 0.0
        ds = ds[mask]
        sentiment_avg = np.mean(ds)
        sentiment_std = np.std(ds)
        sentiment_median = np.median(ds)
        time = datetime.strptime(t + '-1', "%Y_%W-%w")
        for user in users:
            dts = np.array(data[t][user]["dt"])/3600
            dt = np.mean(dts)
            ats = np.array(data[t][user]["activation_time"])
            ats = np.sort(ats)
            dats = np.diff(ats)
            '''
            datsnew = []
            for dat in dats:
                if dat > 86400/3:
                    datsnew.append(dat-86400/3)
                else:
                    datsnew.append(dat)
            '''
            at = np.mean(dats)/3600
            dr = data[t][user]["w2v"]
            s = np.array(data[t][user]["excitement"])
            mask = s != 0.0
            s = s[mask]
            excitement = np.mean(s)
            compression = data_compression[t][user]
            xs.append({"time":time,"yw":t,"m":dr,"dt":dt,"at":at,"user":user,"excitement":excitement,"compression":compression})
    df = pd.DataFrame(xs)
    return df


def main_no_events(kind,event_chosen):
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
        v0 = v-timedelta(days = 7)
        v0.replace(tzinfo = utc_tmzone)
        year = v0.year
        week = v0.isocalendar()[1]
        dict_events[k] = [str(year)+"_"+str(week)]
        v_1 = v0-timedelta(days = 7)
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
    output_data = []
    for year_week in tqdm(year_weeks):
        tdf = df[df["yw"] == year_week]
        yname = tdf["yw_name"].unique().tolist()[0]
        graph = nx.read_gpickle("data/network/network_user_{kind}_{year_week}.gpickle".format(kind = kind,year_week = year_week))
        #omega = get_omega(graph)
        nodes = list(graph.nodes())
        users = tdf["user"].tolist()
        dict_user_value = {row["user"]:row["m"] for _,row in tdf.iterrows()}
        dict_user_compression = {row["user"]:row["compression"] for _,row in tdf.iterrows()}
        for user in users:
            total = 0.0
            v = 0.0
            v_compression = 0.0
            if user not in nodes:
                continue
            for neighbor in graph.neighbors(user):
                if neighbor in dict_user_value:
                    v += dict_user_value[neighbor]
                    v_compression += dict_user_compression[neighbor]
                    total+=1
            if total == 0:
                continue
            '''
            i = dict_node_id[user]
            for oth_user in users:
                if oth_user not in nodes:
                    continue
                if oth_user == user:
                    continue
                #dist = nx.resistance_distance(graph,user,oth_user)
                j = dict_node_id[oth_user]
                dist = get_resistance_distance(omega,i,j)
                total += dist
                v += dist*dict_user_value[oth_user]
            '''
            value_user = dict_user_value[user]
            value_neighbors = v/total
            value_compression_neigh = v_compression/total
            dt = tdf[tdf["user"]==user]["dt"].tolist()[0]
            at = tdf[tdf["user"]==user]["at"].tolist()[0]
            excs = tdf[tdf["user"]==user]["excitement"].tolist()[0]
            compression = tdf[tdf["user"]==user]["compression"].tolist()[0]
            deg = graph.degree(user)
            indegree = graph.in_degree(user)
            outdegree = graph.out_degree(user)
            output_data.append({"yw_name":yname,"year_week":year_week,"user":user,"value_user":value_user,"value_neighbors":value_neighbors,"dt":dt,"at":at,"excitement":excs,"compression":compression,"compression_neigh":value_compression_neigh,"degree":deg,"indegree":indegree,"outdegree":outdegree})
    df = pd.DataFrame(output_data)
    df.to_csv("data/to_plot/stat_neighbors_users_{kind}.csv".format(kind=kind),sep = ",",index = False)



def main(kind,event_chosen):
    if kind == "europe":
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
    output_data = []
    for year_week in tqdm(year_weeks):
        tdf = df[df["yw"] == year_week]
        yname = tdf["yw_name"].unique().tolist()[0]
        graph = nx.read_gpickle("data/network/network_user_{kind}_{year_week}.gpickle".format(kind = kind,year_week = year_week))
        #omega = get_omega(graph)
        nodes = list(graph.nodes())
        users = tdf["user"].tolist()
        dict_user_value = {row["user"]:row["m"] for _,row in tdf.iterrows()}
        dict_user_compression = {row["user"]:row["compression"] for _,row in tdf.iterrows()}
        for user in users:
            total = 0.0
            v = 0.0
            v_compression = 0.0
            if user not in nodes:
                continue
            for neighbor in graph.neighbors(user):
                if neighbor in dict_user_value:
                    v += dict_user_value[neighbor]
                    v_compression += dict_user_compression[neighbor]
                    total+=1
            if total == 0:
                continue
            '''
            i = dict_node_id[user]
            for oth_user in users:
                if oth_user not in nodes:
                    continue
                if oth_user == user:
                    continue
                #dist = nx.resistance_distance(graph,user,oth_user)
                j = dict_node_id[oth_user]
                dist = get_resistance_distance(omega,i,j)
                total += dist
                v += dist*dict_user_value[oth_user]
            '''
            value_user = dict_user_value[user]
            value_neighbors = v/total
            value_compression_neigh = v_compression/total
            dt = tdf[tdf["user"]==user]["dt"].tolist()[0]
            at = tdf[tdf["user"]==user]["at"].tolist()[0]
            excs = tdf[tdf["user"]==user]["excitement"].tolist()[0]
            compression = tdf[tdf["user"]==user]["compression"].tolist()[0]
            deg = graph.degree(user)
            indegree = graph.in_degree(user)
            outdegree = graph.out_degree(user)
            output_data.append({"yw_name":yname,"year_week":year_week,"user":user,"value_user":value_user,"value_neighbors":value_neighbors,"dt":dt,"at":at,"excitement":excs,"compression":compression,"compression_neigh":value_compression_neigh,"degree":deg,"indegree":indegree,"outdegree":outdegree})
    df = pd.DataFrame(output_data)
    df.to_csv("data/to_plot/stat_neighbors_users_{kind}.csv".format(kind=event_chosen_string),sep = ",",index = False)


main("nba","NBA Trades")
main("politics","US 2020")
main("nfl","NFL Kickoff Game")
main("europe","Brexit")
main("europe","US 2020")


main_no_events("nba","NBA Trades")
main_no_events("politics","US 2020")
main_no_events("nfl","NFL Kickoff Game")
main_no_events("europe","Brexit")
main_no_events("europe","US 2020")

#supplementary
main("nba","NBA Restart")
main("nba","Orlando")
main("politics","Capitol Hill")
main("politics","Trump")
main("nfl","SuperBowl LIV")
main("nfl","NFL Draft")
main("europe","Capitol Hill")
