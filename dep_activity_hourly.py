import pandas as pd
import pytz
import json
import seaborn as sns
from scipy.stats import zscore
import numpy as np
from datetime import datetime,timedelta
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Cairo')
matplotlib.style.use("fast")
centrimeters = 1/2.54
def plot_data(kind,title):
    dict_color = {
        "nfl":["#6F1980","#4DB6CB"],
        "politics":["#0A2F5C","#D94576"],
        "nba":["#538F4D","#7026BA"],
        "europe":["#855247","#4D7999"]
    }
    dict_color_other = {
        "nfl":["#A92BC2","#1B8398"],
        "politics":["#2666BA","#E68AA7"],
        "nba":["#9ECB9A","#B484EB"],
        "europe":["#A96D60","#37566D"]
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
    y = 210*(1/3)
    x = 297*(1/2)
    fig = plt.figure(figsize = (x*centrimeters,y*centrimeters))
    fontsize = 112
    ax = fig.add_subplot(1,1,1)
    with open("data/distribution/hour_interactions_"+kind+".json","r") as inpuf:
        data = json.load(inpuf)
    year_weeks = ["2020_"+str(i) for i in range(1,54)]
    for i in range(1,5):
        year_weeks.append("2021_"+str(i))
    dict_yw = {year_week:id for (id,year_week) in enumerate(year_weeks)}
    t_data = []
    for year_week in year_weeks:
        d = data[year_week]
        total = np.sum(list(d.values()))
        hist = np.zeros(24)
        for (k,v) in d.items():
            hist[int(k)] = v/total
        t_data.append(hist)
    zs = zscore(t_data, axis = None)
    ls = ["solid","dashed"]
    t_plot = {0:[],1:[]}
    for event in dict_reddit_events[kind]:
        for id,week in enumerate(dict_events[event]):
            id_z = dict_yw[week]
            z = zs[id_z]
            t_plot[id].append(z)
    dict_plot = {k:np.mean(v,axis = 0) for (k,v) in t_plot.items()}
    labels = ["Event","Week Before"]
    lws = [8,6]
    xbin = np.arange(24)
    #filbetween
    fill_plot = {k:np.std(v,axis = 0) for (k,v) in t_plot.items()}
    for (k,v) in fill_plot.items():
        color_other = dict_color_other[kind][k]
        upper = dict_plot[k]+v
        lower= dict_plot[k]-v
        ax.fill_between(xbin,upper,lower,color = color_other,alpha = 0.3)
    '''
    for (k,v) in t_plot.items():
        for x in v:
            color_other = dict_color_other[kind][k]
            ax.plot(xbin,x,lw = lws[k],ls = ls[k],color = color_other)
    '''
    for (k,v) in dict_plot.items():
        color = dict_color[kind][k]
        ax.plot(xbin,v,lw = 20,ls = ls[k],color = color,label = labels[k])
    ax.set_ylabel("Activity",fontsize = fontsize)
    ax.set_xlabel("Hour",fontsize = fontsize)
    ax.tick_params(axis='both', which='major', labelsize = 64,size = 48)
    ax.tick_params(axis='both', which='minor', labelsize = 64,size = 48)
    ax.legend(fontsize = fontsize*0.7, loc = 0,ncol = 2,edgecolor = "grey")
    fig.suptitle(title, fontsize = fontsize)
    #
    fig.tight_layout(rect = (0.0,0.0,1.0,0.98))
    fig.savefig("fig/distrib_activity_hourly/"+kind+".pdf")

plot_data("nba","NBA")
plot_data("politics","U.S. Politics")
plot_data("europe","Europe")
plot_data("nfl","NFL")
