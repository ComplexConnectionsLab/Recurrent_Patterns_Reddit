import pandas as pd
import pytz
from datetime import datetime,timedelta
from scipy.stats import skew,kurtosis
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.dates as mdates
import json
import numpy as np
matplotlib.use('Cairo')
matplotlib.style.use("fast")
centrimeters = 1/2.54

def plot_data():
    dict_title = {"nfl":"NFL","nba":"NBA","politics":"U.S. Politics","europe":"Europe"}
    dict_limits = {
        "nfl":[(4,22),(0,900),(0.12,0.22)],
        "nba":[(1.8,18),(0,800),(0.10,0.25)],
        "politics":[(2,16),(100,500),(0.15,0.3)],
        "europe":[(2,6),(10,50),(0.10,0.15)]
    }
    kinds = ["politics","nba","nfl","europe"]
    dict_color = {
        "politics":["#BF000D","#E53844","#990A13"],
        "nfl":["#FFCE2B","#FFDE70","#E0AC00"],
        "nba":["#DD802F","#E6A267","#A65F21"],
        "europe":["#2A8000","#00A336","#226600"],
    }
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
        dict_events[k] = v
        year = v.year
        week = v.isocalendar()[1]
        dict_events[k] = str(year)+"_"+str(week)
    dict_reddit_events = {
            "europe":["Brexit","Cyprus","Belarus Protest","Lockdown Ease","US 2020","Capitol Hill","Coronavirus"],
            "politics":["Trump","Trump Covid","US 2020","Capitol Hill","Coronavirus","BLM"],
            "nba":["Kobe Bryant","NBA Stop","NBA Restart","Orlando","NBA Finals","NBA Trades"],
            "nfl":["NFL Draft","NFL Kickoff Game","NFL PlayOff 2020","SuperBowl LIV","NFL Trades","NFL PlayOff"]
        }
    dict_reddit_events = {k:[dict_events[v] for v in vs] for (k,vs) in dict_reddit_events.items()}
    #
    y = 210*(2/3)
    x = 297*(1/3)
    #
    for id,kind in enumerate(kinds):
        fig = plt.figure(figsize = (x*centrimeters,y*centrimeters))
        fontsize = 70
        color = dict_color[kind][0]
        ax = fig.add_subplot(1,1,1)
        with open("data/distribution/interactions_"+kind+".json","r") as inpuf:
            data = json.load(inpuf)
        ndata = []
        for (k,ls) in data.items():
            ys = np.array(ls)
            ys = ys/3600
            r = datetime.strptime(k + '-1', "%Y_%W-%w")
            m = np.mean(np.log10(ys))
            sig = np.var(np.log10(ys))
            if k in dict_reddit_events[kind]:
                week = "Event"
            else:
                week = "No Event"
            ndata.append({
                "date":r,
                "week":week,
                "x":m,
                "y":sig
            })
        df = pd.DataFrame(ndata)
        df = df.sort_values(by = ["date"])
        df = df.drop_duplicates(subset = ["date"])
        xdf = df[df["week"] == "No Event"]
        ax.scatter(xdf["x"],xdf["y"],s = 3500,alpha = 0.7,c = color)
        xdf = df[df["week"] == "Event"]
        ax.scatter(xdf["x"],xdf["y"],s = 3500,marker = "^",alpha = 0.7,c = color)
        ax.set_ylabel("Std(Δt)",fontsize = fontsize,labelpad = 40)
        ax.set_xlabel("Mean",fontsize = fontsize,labelpad = 32)
        ax.tick_params(axis='both', which='major', labelsize = 64,size = 48)
        ax.tick_params(axis='both', which='minor', labelsize = 64,size = 48)
        ax.set_title(dict_title[kind], fontsize = fontsize)
        fig.subplots_adjust(hspace=0.2,top = 0.95,left = 0.2,right = 0.8)
        fig.tight_layout(rect = (0.05,0.05,0.95,0.95))
        fig.savefig("fig/time_metrics/"+kind+"_scatter.pdf")


plot_data()