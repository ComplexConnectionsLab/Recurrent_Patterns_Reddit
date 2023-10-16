import pandas as pd
import pytz
from datetime import datetime,timedelta
import json
import numpy as np
from distfit import distfit
from scipy import stats


def compute_data(kind):
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
    dict_reddit_events = {
        "europe":["Brexit","Cyprus","Belarus Protest","Lockdown Ease","US 2020","Capitol Hill","Coronavirus"],
        "politics":["Trump","Trump Covid","US 2020","Capitol Hill","Coronavirus","BLM"],
        "nba":["Kobe Bryant","NBA Stop","NBA Restart","Orlando","NBA Finals","NBA Trades"],
        "nfl":["NFL Draft","NFL Kickoff Game","NFL PlayOff 2020","SuperBowl LIV","NFL Trades","NFL PlayOff"]
    }

    dict_event = {}
    dict_events = {}
    for (k,v) in tmp.items():
        v.replace(tzinfo = utc_tmzone)
        year = v.year
        week = v.isocalendar()[1]
        dict_events[k] = [str(year)+"_"+str(week)]
        dict_event[k] = v
        v_1 = v-timedelta(days = 7)
        year = v_1.year
        week = v_1.isocalendar()[1]
        if str(year)+"_"+str(week) == "2021_53":
            dict_events[k].append("2020_53")
        else:
            dict_events[k].append(str(year)+"_"+str(week))
    #
    with open("data/distribution/interactions_"+kind+".json","r") as inpuf:
        data = json.load(inpuf)
    labels = ["Event","Week Before"]
    events = dict_reddit_events[kind]
    for event in events:
        for id,w in enumerate(dict_events[event]):
            d = data[w]
            d = np.array(d)
            d = d+0.00000000001
            d = d/3600
            model = distfit(bound='both',todf = True,distr='lognorm')
            model.fit_transform(d)
            sigma, loc, scale = stats.lognorm.fit(d, floc=0)
            print(sigma,loc,scale)
            res = stats.kstest(d,"lognorm",args=(sigma, 0, scale),alternative='two-sided',mode='approx')
            print(model)
            print(res)



#compute_data("nba")
