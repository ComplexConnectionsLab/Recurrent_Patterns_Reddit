import pandas as pd
import pytz
import json
from itertools import combinations
import seaborn as sns
import numpy as np
from datetime import datetime,timedelta
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
matplotlib.use('Cairo')
matplotlib.style.use("fast")
centrimeters = 1/2.54


def jaccard_sim(list_x,list_y):
    set_x = set(list_x)
    set_y = set(list_y)
    nominator = set_x.intersection(set_y)
    denominator = set_x.union(set_y)
    return len(nominator)/len(denominator)


def get_ngrams(kind):
    year_weeks = ["2020_"+str(i) for i in range(1,54)]
    for i in range(1,5):
        year_weeks.append("2021_"+str(i))
    patterns = {}
    tmp_week = {}
    id_pattern = 0
    xs = []
    for year_week in year_weeks:
        with open("data/ngrams/"+kind+"_"+year_week+".csv","r") as inpuf:
            df = pd.read_csv(inpuf)
        z_scores = []
        for _,row in df.iterrows():
            yt = row[[str(y) for y in range(100)]]
            if yt.std() == 0.0:
                continue
            z_score = (row["how_many_times"]-yt.mean())/yt.std()
            z_scores.append({"pattern":row["pattern"],"z_score":z_score})
        z_df = pd.DataFrame(z_scores)
        z_df = z_df.sort_values(by = ["z_score"],ascending = False)
        how_many = int(z_df.shape[0]*0.15)
        z_df = z_df.head(how_many)
        z_scores = {}
        for _,row in z_df.iterrows():
            z_scores[row["pattern"]] = row["z_score"]
            if row["pattern"] not in patterns:
                patterns[row["pattern"]] = id_pattern
                id_pattern +=1
        tmp_week[year_week] = z_scores
        xs.append(datetime.strptime(year_week + '-1', "%Y_%W-%w"))
    #normalize data
    week_data = {}
    for (week,data) in tmp_week.items():
        week_data[week] = np.zeros(id_pattern)
        for (pattern,z_score) in data.items():
            week_data[week][patterns[pattern]] = z_score
        norm = np.linalg.norm(week_data[week])
        week_data[week] = week_data[week]/norm
    tmp = np.array([v for v in week_data.values()])
    pairwise_similarity = tmp.dot(tmp.T)
    output_data = []
    for x in range(0,len(year_weeks)):
        for y in range(0,len(year_weeks)):
            if x == y:
                continue
            output_data.append({"x":xs[x],"y":xs[y],"value":1-pairwise_similarity[x,y]})
    df = pd.DataFrame(output_data)
    return df


def get_ngrams_jaccard(kind):
    year_weeks = ["2020_"+str(i) for i in range(1,54)]
    for i in range(1,5):
        year_weeks.append("2021_"+str(i))
    patterns = {}
    tmp_week = {}
    id_pattern = 0
    xs = []
    all_patterns = []
    for year_week in year_weeks:
        with open("data/ngrams/"+kind+"_"+year_week+".csv","r") as inpuf:
            df = pd.read_csv(inpuf)
        z_scores = []
        for _,row in df.iterrows():
            yt = row[[str(y) for y in range(100)]]
            yt = yt.to_numpy()
            if yt.std() == 0.0:
                continue
            z_score = (row["how_many_times"]-yt.mean())#/yt.std()
            z_scores.append({"pattern":row["pattern"],"z_score":z_score})
        z_df = pd.DataFrame(z_scores)
        z_df = z_df.sort_values(by = ["z_score"],ascending = False)
        #how_many = int(z_df.shape[0]*0.90)
        how_many = z_df.shape[0]
        threshold = z_df["z_score"].mean()
        z_df = z_df[z_df["z_score"]>threshold]
        print(z_df.shape[0]/how_many)
        #z_df = z_df.head(how_many)
        z_scores = {}
        for _,row in z_df.iterrows():
            z_scores[row["pattern"]] = row["z_score"]
            if row["pattern"] not in patterns:
                patterns[row["pattern"]] = id_pattern
                id_pattern +=1
        tmp_week[year_week] = [row["pattern"] for _,row in z_df.iterrows()]
        all_patterns.append([row["pattern"] for _,row in z_df.iterrows()])
        xs.append(datetime.strptime(year_week + '-1', "%Y_%W-%w"))
    #
    aps = []
    for c in combinations(all_patterns,2):
        s0 = set(c[0])
        s1 = set(c[1])
        nps = list(set(s0).intersection(s1))
        for npx in nps:
            aps.append(npx)
    all_patterns = list(set(aps))
    print(len(all_patterns))
    pairwise_similarity = np.zeros((len(year_weeks),len(year_weeks)))
    for x,year_week_x in enumerate(year_weeks):
        for y,year_week_y in enumerate(year_weeks):
            px = [p for p in tmp_week[year_week_x]] #if p not in all_patterns]
            py = [p for p in tmp_week[year_week_y]] #if p not in all_patterns]
            #print(len(tmp_week[year_week_x]))
            #print(len(px))
            #print(len(tmp_week[year_week_y]))
            #print(len(py))
            #print("#"*128)
            jsim_value = jaccard_sim(px,py)
            pairwise_similarity[x,y] = jsim_value
    output_data = []
    for x in range(0,len(year_weeks)):
        for y in range(0,len(year_weeks)):
            if x == y:
                continue
            output_data.append({"x":xs[x],"y":xs[y],"value":pairwise_similarity[x,y]})
    df = pd.DataFrame(output_data)
    print(df)
    return df


def plot_data(kind,title):
    dict_color = {
        "nfl":"#4DB6CB",
        "politics":"#D94576",
        "nba":"#538F4D",
        "europe":"#855247"
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
        v_1 = v+timedelta(days = 7)
        year = v_1.year
        week = v_1.isocalendar()[1]
        dict_events[k].append(str(year)+"_"+str(week))
        v_1 = v-timedelta(days = 7)
        year = v_1.year
        week = v_1.isocalendar()[1]
        dict_events[k].append(str(year)+"_"+str(week))
    y = 250*(1/2)
    x = 350*(1/2)
    fig = plt.figure(figsize = (x*centrimeters,y*centrimeters))
    fontsize = 120
    ax_up = fig.add_subplot(1,1,1)
    #pattern / ngrams
    color = dict_color[kind]
    df = get_ngrams_jaccard(kind)
    df = df.drop_duplicates(subset=["x","y"])
    ####################################
    S = 1_00
    df["value"] = pd.cut(df["value"],[i/S for i in range(0,S+1)],labels = [i/S for i in range(0,S)])
    df["value"] = pd.to_numeric(df["value"])
    df["cat"] = df["x"]>df["y"]
    df = df[df["cat"]]
    ####################################
    pal = sns.color_palette("light:"+color, as_cmap=True)
    ####################################
    g = sns.relplot(data = df, x = "x",y = "y",
                    size = "value",
                    hue = "value",
                    size_norm = (0.0, 1.0),
                    hue_norm = (0.0,1.0),
                    sizes = (4_000,4_000),
                    marker = "s",
                    palette = pal,alpha = 0.7,
                    height = 64, aspect = 64/64)
    ax_up = g.ax
    fig = g.fig
    ax_up.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax_up.yaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax_up.tick_params(axis='both', which='major', labelsize = 96,size = 64)
    ax_up.tick_params(axis='both', which='minor', labelsize = 96,size = 64)
    #
    handles, labels = ax_up.get_legend_handles_labels()
    #ax_up.legend(handles = handles[2:], labels = labels[2:],fontsize = fontsize*0.5, loc = 7,ncol = 2,edgecolor = "grey",markerscale = 10)
    ax_up.legend(handles = handles[2:], labels = labels[2:],fontsize = fontsize*0.65,bbox_to_anchor=[1.1, 0.5],loc='center right', frameon=False)
    #
    fig.suptitle("Word Similarity: "+title, fontsize = fontsize)
    #
    #fig.tight_layout(rect=[0.05, 0.05, 0.95, 0.95])
    fig.subplots_adjust(top = 0.9, bottom = 0.15,left = 0.15,right = 0.9)
    fig.savefig("fig/word_similarity/relplot_"+kind+"_jc.pdf")
    '''
    pal = sns.color_palette("light:"+color, as_cmap=True)
    g = sns.relplot(data = df, x = "x",y = "y",size = "value",hue = "value",
                    size_norm=(0.0, 1.0),hue_norm = (0.0,1.0),
                    sizes = (500,6_000),edgecolor = ".5",
                    palette = pal,alpha = 0.7,
                    height = 64, aspect = 64/64)
    g._legend.remove()
    ax_up = g.ax
    fig = g.fig
    ax_up.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax_up.yaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax_up.tick_params(axis='both', which='major', labelsize = 96,size = 64)
    ax_up.tick_params(axis='both', which='minor', labelsize = 96,size = 64)
    g.ax.margins(.02)
    ####################################
    #patch
    dict_events_patch = {"nfl":["NFL Kickoff Game","NFL PlayOff"],"nba":["Orlando","NBA Finals"],"politics":["Trump Covid","US 2020"]}
    if kind in dict_events_patch:
        startTime = dict_event[dict_events_patch[kind][0]]
        endTime = dict_event[dict_events_patch[kind][1]]
        # convert to matplotlib date representation
        start = mdates.date2num(startTime)
        if kind == "politics":
            end = mdates.date2num(endTime+timedelta(days=9))
        else:
            end = mdates.date2num(endTime-timedelta(days=2))
        width = end - start
        startx = start
        starty = datetime(2020,1,1)
        endy = datetime(2021,1,31)
        start = mdates.date2num(starty)
        end = mdates.date2num(endy)
        height = end - start
        starty = start
        # Plot rectangle
        rect = Rectangle((startx, starty), width, height,lw = 14, color = "#C02638",ls = "dashed",fill = False)
        ax_up.add_patch(rect)
        rect = Rectangle((starty, startx), height, width,lw = 14, color = "#C02638",ls = "dashed",fill = False)
        ax_up.add_patch(rect)
    ####################################
    dict_single_event = {"politics":["Coronavirus",10],"nba":["NBA Trades",7]}
    if kind in dict_single_event:
        startTime = dict_event[dict_single_event[kind][0]]
        endTime = startTime+timedelta(days=dict_single_event[kind][1])
        # convert to matplotlib date representation
        start = mdates.date2num(startTime)
        end = mdates.date2num(endTime-timedelta(days=2))
        width = end - start
        startx = start
        starty = datetime(2020,1,1)
        endy = datetime(2021,1,31)
        start = mdates.date2num(starty)
        end = mdates.date2num(endy)
        height = end - start
        starty = start
        # Plot rectangle
        rect = Rectangle((startx, starty), width, height,lw = 14, color = "#C02638",ls = "dashed",fill = False)
        ax_up.add_patch(rect)
        rect = Rectangle((starty, startx), height, width,lw = 14, color = "#C02638",ls = "dashed",fill = False)
        ax_up.add_patch(rect)

    dict_extra = {"nfl":[datetime(2020,6,4),datetime(2020,7,10)]}
    if kind in dict_extra:
        for ev in dict_extra["nfl"]:
            startTime = ev
            endTime = startTime+timedelta(days=7)
            # convert to matplotlib date representation
            start = mdates.date2num(startTime)
            end = mdates.date2num(endTime)
            width = end - start
            startx = start
            starty = datetime(2020,1,1)
            endy = datetime(2021,1,31)
            start = mdates.date2num(starty)
            end = mdates.date2num(endy)
            height = end - start
            starty = start
            # Plot rectangle
            rect = Rectangle((startx, starty), width, height,lw = 14, color = "#EA9839",ls = "dashed",fill = False)
            ax_up.add_patch(rect)
            rect = Rectangle((starty, startx), height, width,lw = 14, color = "#EA9839",ls = "dashed",fill = False)
            ax_up.add_patch(rect)

    #
    fig.suptitle("Word Similarity: "+title, fontsize = fontsize)
    #
    fig.subplots_adjust(top = 0.95, bottom = 0.07,left = 0.1,right = 0.95)
    fig.savefig("fig/word_similarity/relplot_"+kind+"_jc.pdf")
    '''


plot_data("nfl","NFL")
plot_data("nba","NBA")
plot_data("europe","Europe")
plot_data("politics","U.S. Politics")
