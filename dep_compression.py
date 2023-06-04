import pandas as pd
import pytz
import json
import seaborn as sns
import numpy as np
from datetime import datetime,timedelta
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.patches import FancyBboxPatch
matplotlib.use('Cairo')
matplotlib.style.use("fast")

centrimeters = 1/2.54

def plot_data(kind,title):
    dict_color = {
        "politics":"#0A2F5C",
        "nfl":"#6F1980",
        "nba":"#7026BA",
        "europe":"#779FBB",
    }
    est = pytz.timezone('US/Eastern')
    utc_tmzone = pytz.utc
    tmp = {
        #us
        "Trump\nCOVID-19":datetime(2020,10,2),
        "Trump\nTrial":datetime(2020,2,5),
        "US 2020":datetime(2020,11,3),
        "Capitol\nHill":datetime(2021,1,6),
        "Black\nLives\nMatter":datetime(2020,6,6),
        #covid-19
        "COVID-19":datetime(2020,3,11),
        "Lockdown\nEase":datetime(2020,5,1),
        #eu
        "Brexit":datetime(2020,1,31),
        "Belarus\nProtest":datetime(2020,8,10),
        "Cyprus\nTensions":datetime(2020,9,10),
        #March 11 – COVID-19 pandemic: The World Health Organization declares the COVID-19 outbreak a pandemic.[51]
        #nba
        "NBA\nRestart":datetime(2020,7,31),
        "Finals":datetime(2020,10,11),
        "NBA\nTrades":datetime(2020,11,21),
        "Kobe\nBryant":datetime(2020,1,26),
        "NBA\nStop":datetime(2020,3,12),
        "Regular\nSeason":datetime(2020,12,22),
        #nfl
        "Draft":datetime(2020,4,24),
        "Kickoff\nGame":datetime(2020,9,11),
        "SuperBowl\nLIV":datetime(2020,2,2),
        "NFL\nTrades":datetime(2020,3,18),
        "PlayOff":datetime(2021,1,10),
    }
    dict_events = {}
    for (k,v) in tmp.items():
        v.replace(tzinfo = utc_tmzone)
        dict_events[k] = v
    dict_reddit_events = {
        "europe": ["Brexit","Cyprus\nTensions","Belarus\nProtest","Lockdown\nEase","US 2020","Capitol\nHill","COVID-19"],
        "politics": ["Trump\nTrial","Trump\nCOVID-19","US 2020","Capitol\nHill","COVID-19","Black\nLives\nMatter"],
        "nba":["Kobe\nBryant","NBA\nStop","Regular\nSeason","NBA\nRestart","Finals","NBA\nTrades"],
        "nfl":["Draft","Kickoff\nGame","SuperBowl\nLIV","NFL\nTrades","PlayOff"]
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
    dict_events["Capitol\nHill"] = ["2020_53","2020_52"]
    dict_events["PlayOff"] = ["2020_53","2020_52"]

    #compression
    with open("data/ts_interactions/compression_"+kind+".json","r") as inpuf:
        data = json.load(inpuf)
    ndata = []
    for (k,ls) in data.items():
        ys = np.array([l for (sub,l) in ls.items()])
        r = datetime.strptime(k + '-1', "%Y_%W-%w")
        yw = k
        ndata.append({
            "date":r,
            "mean":np.mean(ys),
            "yw":k
        })
    df = pd.DataFrame(ndata)
    df = df.sort_values(by = ["date"])
    df = df.drop_duplicates(subset = ["date"])
    to_plot = []
    for event in dict_reddit_events[kind]:
        week0 = dict_events[event][0]
        week1 = dict_events[event][1]
        v0 = df[df["yw"] == week0]["mean"].iloc[0]
        v1 = df[df["yw"] == week1]["mean"].iloc[0]
        to_plot.append({"event":event,"value":(v0-v1)*100/v0})
    df["mean"] = df["mean"].diff()*100/df["mean"]
    avg_x = df["mean"].mean()
    std_x = df["mean"].std()/np.sqrt(df.shape[0])
    #to_plot.append({"event":"Average","value":x})
    toplot = pd.DataFrame(to_plot)
    color = dict_color[kind]
    colors = [color for i in range(toplot.shape[0])]
    toplot = toplot.sort_values(by = ["value"]).reset_index()
    toplot["colors"] = colors
    #
    alpha = 5
    y = alpha*210
    x = alpha*297*(0.5)
    fig = plt.figure(figsize = (x*centrimeters,y*centrimeters))
    #
    fontsize = 1_000
    ax = fig.add_subplot(1,1,1)
    ax.axvline(x = avg_x+std_x,color = "#ABACB0",ls = "dashed",lw = 100)
    ax.axvline(x = avg_x-std_x,color = "#ABACB0",ls = "dashed",lw = 100)
    ax.axvspan(avg_x-std_x,avg_x+std_x,color = "#ABACB0", alpha = .33)
    sns.barplot(data = toplot,x = "value",y ="event",ax = ax,orient = "h",saturation = 0.8,palette = toplot["colors"],joinstyle='bevel')
    new_patches = []
    for patch in reversed(ax.patches):
        if isinstance(patch,matplotlib.patches.Polygon):
            continue
        bb = patch.get_bbox()
        color = patch.get_facecolor()
        if np.abs(bb.width) < 1:
            p_bbox = FancyBboxPatch((bb.xmin, bb.ymin+bb.height/4),
                                    abs(bb.width), abs(bb.height/2),
                                    boxstyle="round,pad=-0.0040,rounding_size=0.04",
                                    ec="none", fc=color,
                                    mutation_aspect = 0.2
                                    )
        elif np.abs(bb.width) < 3:
            p_bbox = FancyBboxPatch((bb.xmin, bb.ymin+bb.height/4),
                                    abs(bb.width), abs(bb.height/2),
                                    boxstyle="round,pad=-0.0040,rounding_size=0.4",
                                    ec="none", fc=color,
                                    mutation_aspect = 0.2
                                    )
        else:
            p_bbox = FancyBboxPatch((bb.xmin, bb.ymin+bb.height/4),
                                    abs(bb.width), abs(bb.height/2),
                                    boxstyle="round,pad=-0.0040,rounding_size=0.8",
                                    ec="none", fc=color,
                                    mutation_aspect = 0.2
                                    )
        patch.remove()
        new_patches.append(p_bbox)
    for patch in new_patches:
        ax.add_patch(patch)
    ax.tick_params(axis='both', which='major', labelsize = 800,size = 50)
    ax.set_xlabel("Percent Change of Compression",fontsize = fontsize)
    #ax.set_ylabel("Event",fontsize = fontsize)
    box = ax.get_position()
    box.x0 = box.x0 + 0.07
    box.x1 = box.x1 + 0.07
    ax.set_position(box)
    #
    fig.suptitle(title, fontsize = fontsize,x = 0.57, y = 0.93)
    fig.savefig("fig/compression/"+kind+".pdf")

plot_data("nba","NBA")
plot_data("politics","U.S. Politics")
plot_data("nfl","NFL")
plot_data("europe","Europe")