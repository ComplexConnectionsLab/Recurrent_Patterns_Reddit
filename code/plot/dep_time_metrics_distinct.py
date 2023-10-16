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
def plot_data(kind,title,limits):
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
    dict_reddit_events = {
        "europe":["Brexit","Cyprus","Belarus Protest","Lockdown Ease","US 2020","Capitol Hill","Coronavirus"],
        "politics":["Trump","Trump Covid","US 2020","Capitol Hill","Coronavirus","BLM"],
        "nba":["Kobe Bryant","NBA Stop","NBA Restart","Orlando","NBA Finals","NBA Trades"],
        "nfl":["NFL Draft","NFL Kickoff Game","NFL PlayOff 2020","SuperBowl LIV","NFL Trades","NFL PlayOff"]
    }
    y = 210/2
    x = 297/2
    fig = plt.figure(figsize = (x*centrimeters,y*centrimeters))
    fontsize = 112
    color = dict_color[kind][0]
    #ax1
    ax1 = fig.add_subplot(2,1,1)
    with open("data/distribution/interactions_"+kind+".json","r") as inpuf:
        data = json.load(inpuf)
    ndata = []
    for (k,ls) in data.items():
        ys = np.array(ls)
        ys = ys/3600
        r = datetime.strptime(k + '-1', "%Y_%W-%w")
        m = skew(ys)
        m = kurtosis(ys)
        ndata.append({
            "date":r,
            "y":m,
        })
    df = pd.DataFrame(ndata)
    df = df.sort_values(by = ["date"])
    df = df.drop_duplicates(subset = ["date"])
    ax1.scatter(df["date"],df["y"],s = 3500,alpha = 0.7,c = color)
    ax1.set_ylabel("γ₁(Δt) [min]",fontsize = fontsize)
    #ax1.set_xlabel("Date",fontsize = fontsize)
    #ax1.set_ylim(limits[0])
    #second
    ax2 = fig.add_subplot(2,1,2)
    tax = ax2.twinx()
    color = dict_color[kind][1]
    #interactions
    with open("data/ts_week_after/dtw_interactions_"+kind+".json","r") as inpuf:
        data = json.load(inpuf)
    ndata = []
    for (k,ls) in data.items():
        m = np.mean(ls)
        r = datetime.strptime(k + '-1', "%Y_%W-%w")
        ndata.append({"date":r,"mean":m})
    df = pd.DataFrame(ndata)
    df = df.sort_values(by = ["date"])
    df = df.drop_duplicates(subset = ["date"])
    dtw_plot = ax2.plot(df["date"],df["mean"],lw = 20, color = color,ls = "solid", label = "DTW")
    ax2.set_ylabel("DTW",fontsize = fontsize)
    ax2.set_xlabel("Date",fontsize = fontsize)
    ax2.set_ylim(limits[1])
    #coherence
    color = dict_color[kind][2]
    with open("data/ts_week_after/coherence_interactions_"+kind+".json","r") as inpuf:
        data = json.load(inpuf)
    ndata = []
    for (k,ls) in data.items():
        if k == "f":
            continue
        ys = np.array(ls)
        coherences_week = np.array(ls)
        removed_zero_coh = coherences_week[:,1:]
        means_over_omega = np.mean(removed_zero_coh,axis = 1)
        true_mean = np.mean(means_over_omega)
        r = datetime.strptime(k + '-1', "%Y_%W-%w")
        ndata.append({"date":r,"mean":true_mean})
    df = pd.DataFrame(ndata)
    df = df.sort_values(by = ["date"])
    df = df.drop_duplicates(subset = ["date"])
    coh_plot = tax.plot(df["date"],df["mean"],lw = 20, color = color,ls = "dashed",label = "Coherence")
    tax.set_ylabel("Coherence",fontsize = fontsize,rotation = 270, labelpad = 100)
    #
    for ax in [ax1,ax2,tax]:
        ax.tick_params(axis='both', which='major', labelsize = 64,size = 48)
        ax.tick_params(axis='both', which='minor', labelsize = 64,size = 48)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        if ax in [ax2,tax]:
            continue
        if ax == ax1:
            ax.set_xticklabels([])
        #add vertical line
        ylow, yup = ax.get_ylim()
        for event in dict_reddit_events[kind]:
            d = dict_events[event]
            ax.axvline(d,ymin = 0.05,ymax = 0.87, c = "#585B6E", lw = 10,ls = "dashdot")
        #ax.text(d,yup,event,verticalalignment='center',fontsize = fontsize)
    lns = coh_plot + dtw_plot
    labs = [l.get_label() for l in lns]
    if kind == "politics":
        ax.legend(lns, labs,fontsize = fontsize*0.8, loc = 9,ncol = 2,edgecolor = "grey")
    else:
        ax.legend(lns, labs,fontsize = fontsize*0.8, loc = 0,ncol = 2,edgecolor = "grey")
    ax.set_ylim(limits[-1])
    fig.suptitle(title, fontsize = fontsize)
    #
    fig.subplots_adjust(hspace=0.1,top = 0.92)
    #fig.tight_layout(rect = (0.0,0.0,1.0,0.98))
    fig.savefig("fig/time_metrics/"+kind+".pdf")



plot_data("nfl","NFL",[(2,3.8),(0,900),(0.12,0.22)])
plot_data("nba","NBA",[(1.6,3.2),(0,800),(0.10,0.25)])
plot_data("politics","U.S. Politics",[(1.6,3.4),(100,500),(0.15,0.3)])
plot_data("europe","Europe",[(1.5,2.4),(10,50),(0.10,0.15)])
