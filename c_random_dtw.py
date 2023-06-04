import json
from tqdm import tqdm
from itertools import product
import numpy as np
import pytz
from datetime import datetime,timedelta


def DTWDistance(s1, s2):
    DTW={}

    for i in range(len(s1)):
        DTW[(i, -1)] = float('inf')
    for i in range(len(s2)):
        DTW[(-1, i)] = float('inf')
    DTW[(-1, -1)] = 0

    for i in range(len(s1)):
        for j in range(len(s2)):
            dist= (s1[i]-s2[j])**2
            DTW[(i, j)] = dist + min(DTW[(i-1, j)],DTW[(i, j-1)], DTW[(i-1, j-1)])

    return np.sqrt(DTW[len(s1)-1, len(s2)-1])


def create_data_interactions(database,what_week,output_data):
    with open("data/ts_interactions/interactions_random_"+database+".json","r") as inpuf:
        data_trees = json.load(inpuf)
    year_weeks = [(2020,i) for i in range(1,54)]
    for i in range(1,5):
        year_weeks.append((2021,i))
    seq_weeks = {year_weeks[i+1]:[year_weeks[i],year_weeks[i+1]] for i in range(0,len(year_weeks)-1)}
    key_seq_week = (int(what_week.split("_")[0]),int(what_week.split("_")[1]))
    seq_week = seq_weeks[key_seq_week]
    key_1 = str(seq_week[0][0])+"_"+str(seq_week[0][1])
    key_2 = str(seq_week[1][0])+"_"+str(seq_week[1][1])
    ts_1 = data_trees[key_1].keys()
    ts_2 = data_trees[key_2].keys()
    output_data[what_week] = {}
    for i in tqdm(range(0,100),total = 100):
        output_data[what_week][i] = []
        for c in product(ts_1,ts_2):
            y1 = data_trees[key_1][c[0]]["data"][i]
            y2 = data_trees[key_2][c[1]]["data"][i]
            Cxy = DTWDistance(y1, y2)
            output_data[what_week][i].append(Cxy)
    return output_data


def main(database,what_event):
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
        dict_events[k] = str(year)+"_"+str(week)
    output_data = {}
    what_week = dict_events[what_event]
    output_data = create_data_interactions(database,what_week,output_data)
    with open("data/ts_week_after/dtw_random_interactions_"+database+".json","w") as outpuf:
        json.dump(output_data,outpuf)


main("politics","US 2020")




