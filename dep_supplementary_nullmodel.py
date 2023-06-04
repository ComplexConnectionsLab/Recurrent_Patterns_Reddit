import json
import pytz
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime,timedelta
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
from matplotlib.ticker import MaxNLocator
import matplotlib.patches as mpatches
matplotlib.use('Cairo')
matplotlib.style.use("fast")
centrimeters = 1/2.54


def plot_data(kind,event):
    dict_colors = {"nba":["#DD802F","#802FDD"],"nfl":["#FFCE2B","#4DB6CB"],"politics":["#D8322B","#3C87BC"],"europe":["#2A8000","#4D7999"]}
    dict_colors_nullmodel = {"nba":["#C19D86","#9C7EC9"],"nfl":["#D3C59C","#94B9C7"],"politics":["#D27484","#4D6EA8"],"europe":["#3DB800","#779DBB"]}
    colors = dict_colors[kind]
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
    dict_events_week_before = {}
    for (k,v) in tmp.items():
        v.replace(tzinfo = utc_tmzone)
        year = v.year
        week = v.isocalendar()[1]
        dict_events[k] = str(year)+"_"+str(week)
        v = v -timedelta(days = 7)
        year = v.year
        week = v.isocalendar()[1]
        dict_events_week_before[k] = str(year)+"_"+str(week)

    with open("data/ts_interactions/interactions_"+kind+".json","r") as inpuf:
        data_trees = json.load(inpuf)
    y = 210/2
    x = 297/2
    fontsize = 112
    fig = plt.figure(figsize = (x*centrimeters,y*centrimeters))
    gs = gridspec.GridSpec(2, 1)
    '''
    ax1 = fig.add_subplot(gs[:,0])
    x = dict_events[event]
    datum_trees = [v["data"] for (k,v) in data_trees[str(x)].items()]
    color = colors[0]
    ts_week = np.array(datum_trees)
    means = np.mean(ts_week,axis = 0)
    std = np.std(ts_week,axis = 0)
    df = pd.DataFrame()
    df["mean"] = means
    df["std"] = std
    df["up"] = means+std
    df["low"] = means-std
    today = datetime(2020,1,1,0,0,0)
    maximum = int(df["up"].max()*(1+0.1))
    df["ts"] = [today + x for x in pd.timedelta_range(start = "0 min", end = "24 hour", freq = "5 min")[:-1]]
    ax1.plot(df["ts"],df["mean"],color = color,lw = 20,label = "US 2020")
    ax1.fill_between(df["ts"],df["low"],df["up"], color = color, alpha = 0.4)
    x = dict_events_week_before[event]
    datum_trees = [v["data"] for (k,v) in data_trees[str(x)].items()]
    color = colors[1]
    ts_week = np.array(datum_trees)
    means = np.mean(ts_week,axis = 0)
    std = np.std(ts_week,axis = 0)
    df["mean"] = means
    df["std"] = std
    df["ts"] = [today + x for x in pd.timedelta_range(start = "0 min", end = "24 hour", freq = "5 min")[:-1]]
    ax1.plot(df["ts"],df["mean"],color = color,lw = 20,label = "Week Before")
    ax1.fill_between(df["ts"],df["mean"]-df["std"],df["mean"]+df["std"], color = color, alpha = 0.4)
    '''
    #event week
    colors = dict_colors_nullmodel[kind]
    ax2 = fig.add_subplot(gs[0])
    with open("data/ts_week_after/coherence_random_interactions_"+kind+".json","r") as inpuf:
        data = json.load(inpuf)
    x = dict_events[event]
    data = data[x]
    for (k,v) in data.items():
        coherences_week = np.array(v)
        removed_zero_coh = coherences_week[:,1:]
        means_over_omega = np.mean(removed_zero_coh,axis = 1)
        sns.histplot(data = means_over_omega.tolist(),ax = ax2,
                     stat = "density",color = colors[0],
                     element = "step",fill = False,lw = 0.0,kde = True,line_kws=dict(linewidth = 4,linestyle = (0, (5, 10))),
                     log_scale = False,legend = False,
                     )
    week_patch_random = mpatches.Patch(color=colors[0], label=event + " (Random)",linewidth = 4,linestyle = (0, (5, 10)))
    #true coherence
    with open("data/ts_week_after/coherence_interactions_"+kind+".json","r") as inpuf:
            data = json.load(inpuf)
    data = data[x]
    coherences_week = np.array(data)
    removed_zero_coh = coherences_week[:,1:]
    means_over_omega = np.mean(removed_zero_coh,axis = 1)
    sns.histplot(data = means_over_omega.tolist(),ax = ax2,
                 stat = "density",color = dict_colors[kind][0],
                 element = "step",fill = False,lw = 0.0,kde = True,line_kws=dict(linewidth= 16),
                 log_scale = False,legend = False,
                 )
    week_patch_true = mpatches.Patch(color = dict_colors[kind][0], label=event + " (True)",linewidth= 16)
    #week before
    ax3 = fig.add_subplot(gs[1])
    with open("data/ts_week_after/coherence_random_interactions_"+kind+".json","r") as inpuf:
        data = json.load(inpuf)
    x = dict_events_week_before[event]
    data = data[x]
    for (k,v) in data.items():
        coherences_week = np.array(v)
        removed_zero_coh = coherences_week[:,1:]
        means_over_omega = np.mean(removed_zero_coh,axis = 1)
        sns.histplot(data = means_over_omega.tolist(),ax = ax3,
                     stat = "density",color = colors[1],
                     element = "step",fill = False,lw = 0.0,kde = True,line_kws=dict(linewidth = 4,linestyle = (0, (5, 10))),
                     log_scale = False,legend = False,
                     )
    bweek_patch_random = mpatches.Patch(color = colors[0], label="Week Before (Random)",linewidth = 4,linestyle = "dashed")
    #true coherence
    with open("data/ts_week_after/coherence_interactions_"+kind+".json","r") as inpuf:
        data = json.load(inpuf)
    data = data[x]
    coherences_week = np.array(data)
    removed_zero_coh = coherences_week[:,1:]
    means_over_omega = np.mean(removed_zero_coh,axis = 1)
    sns.histplot(data = means_over_omega.tolist(),ax = ax3,
                 stat = "density",color = dict_colors[kind][1],
                 element = "step",fill = False,lw = 0.0,kde = True,line_kws=dict(linewidth= 16),
                 log_scale = False,legend = False,
                 )
    bweek_patch_true = mpatches.Patch(color = dict_colors[kind][1], label="Week Before (True)",linewidth= 16)
    #font
    '''
    ax1.set_ylabel("Number of Comments",fontsize = fontsize)
    ax1.set_xlabel("t [hour]",fontsize = fontsize)
    ax1.tick_params(axis='both', which='major', labelsize = 64,size = 48)
    ax1.tick_params(axis='both', which='minor', labelsize = 64,size = 48)
    ax1.legend(fontsize = fontsize*0.65, loc = 9,ncol = 2,edgecolor = "grey")
    ax1.set_xlim([today, datetime(2020,1,1,12,0,0)])
    ax1.set_ylim([0,maximum])
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H'))
    '''
    #
    ax2.set_ylabel("Density",fontsize = fontsize*0.85)
    ax2.set_xlabel("Coherence",fontsize = fontsize*0.85)
    ax2.tick_params(axis='both', which='major', labelsize = 54,size = 36)
    ax2.tick_params(axis='both', which='minor', labelsize = 54,size = 36)
    ax3.set_ylabel("Density",fontsize = fontsize*0.85)
    ax3.set_xlabel("Coherence",fontsize = fontsize*0.85)
    ax3.tick_params(axis='both', which='major', labelsize = 54,size = 36)
    ax3.tick_params(axis='both', which='minor', labelsize = 54,size = 36)
    ax3.yaxis.set_major_locator(MaxNLocator(4))
    ax2.yaxis.set_major_locator(MaxNLocator(4))
    #Legend
    ax2.legend([week_patch_random,week_patch_true],[week_patch_random.get_label(),week_patch_true.get_label()],fontsize = fontsize * 0.7)
    ax3.legend([bweek_patch_random,bweek_patch_true],[bweek_patch_random.get_label(),bweek_patch_true.get_label()],fontsize = fontsize * 0.7)
    #title
    #ax1.set_title("Posts",fontsize = fontsize)
    ax2.set_title(event,fontsize = fontsize)
    #
    fig.subplots_adjust(top = 0.95, bottom = 0.09,left = 0.1,right = 0.95)
    if kind == "europe":
        event_chosen_string = "e"+event.replace(" ", "_").lower()
    else:
        event_chosen_string = event.replace(" ", "_").lower()
    fig.savefig("fig/supplementary/null_models/ts_"+event_chosen_string+".pdf")


plot_data("politics","US 2020")
plot_data("nba","NBA Trades")
plot_data("europe","Coronavirus")
plot_data("nfl","NFL Kickoff Game")



'''
plot_data("politics","US 2020")
plot_data("politics","BLM")
plot_data("politics","Capitol Hill")
plot_data("politics","Trump")
#
plot_data("nba","NBA Trades")
plot_data("nba","NBA Restart")
plot_data("nba","NBA Finals")
plot_data("nba","Orlando")
#
plot_data("nfl","SuperBowl LIV")
plot_data("nfl","NFL Kickoff Game")
plot_data("nfl","NFL Draft")
#
plot_data("europe","US 2020")
plot_data("europe","Brexit")
plot_data("europe","Capitol Hill")
'''