import pandas as pd
import pytz
import json
import seaborn as sns
import numpy as np
from datetime import datetime,timedelta
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.dates as mdates
matplotlib.use('Cairo')
matplotlib.style.use("fast")

def plot_data(kind,title):
    dict_color = {
        "nfl":["#C09B7C","#2A868C"],
        "politics":["#184072","#E06790"],
        "nba":["#BC87E8","#75B06F"],
        "europe":["#6F1980","#FFD90F"]
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
        "SuperBowl LIV":datetime(2020,2,2),
        "NFL Trades":datetime(2020,3,18),
        "NFL PlayOff":datetime(2021,1,10),
    }
    dict_events = {}
    for (k,v) in tmp.items():
        v.replace(tzinfo = utc_tmzone)
        dict_events[k] = v
    dict_reddit_events = {
        "europe": ["Brexit","Cyprus","Belarus Protest","Lockdown Ease","US 2020","Capitol Hill","Coronavirus"],
        "politics": ["Trump","Trump Covid","US 2020","Capitol Hill","Coronavirus","BLM"],
        "nba":["Kobe Bryant","NBA Stop","NBA Restart","Orlando","NBA Finals","NBA Trades"],
        "nfl":["NFL Draft","NFL Kickoff Game","SuperBowl LIV","NFL Trades","NFL PlayOff"]
    }
    fig = plt.figure(figsize = (48,32))
    fontsize = 80
    ax = fig.add_subplot(1,1,1)
    with open("data/users/users_degree_"+kind+".json","r") as inpuf:
        data = json.load(inpuf)
    keys = data.keys()
    t_data = []
    for key in keys:
        r = datetime.strptime(key + '-1', "%Y_%W-%w")
        d = data[key]
        v0 = np.array(list(d.values()))
        values = v0[:,0]
        mean = np.mean(values)
        std = np.std(values)/np.sqrt(len(values))
        t_data.append({"value":mean,"upper":mean+std,"lower":mean-std,"date":r})
    df = pd.DataFrame(t_data)
    df = df.sort_values(by = ["date"])
    df = df.drop_duplicates(subset = ["date"])
    color = dict_color[kind][0]
    ax.scatter(df["date"],df["value"],s = 3500,alpha = 0.7,c = color)
    ax.fill_between(df["date"],df["upper"],df["lower"],color = color,alpha = 0.3)
    ax.set_ylabel("Variation Degree",fontsize = fontsize)
    ax.set_xlabel("Date",fontsize = fontsize)
    ax.tick_params(axis='both', which='major', labelsize = 48,size = 32)
    ax.tick_params(axis='both', which='minor', labelsize = 48,size = 32)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    #add vertical line
    ylow, yup = ax.get_ylim()
    for event in dict_reddit_events[kind]:
        d = dict_events[event]
        ax.axvline(d,ymin = 0.05,ymax = 0.87, c = "#585B6E", lw = 10,ls = "dashdot")
    fig.suptitle(title, fontsize = fontsize)
    #
    fig.tight_layout(rect = (0.0,0.0,1.0,0.98))
    fig.savefig("fig/users_variation/variation_degree_"+kind+".png")
    fig.savefig("fig/users_variation/variation_degree_"+kind+".pdf")

plot_data("nba","NBA")
plot_data("politics","U.S. Politics")
plot_data("europe","Europe")
plot_data("nfl","NFL")
