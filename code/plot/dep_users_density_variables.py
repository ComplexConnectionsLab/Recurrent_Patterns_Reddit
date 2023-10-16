import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from scipy import stats
import numpy as np
from matplotlib.ticker import MaxNLocator
import statsmodels.api as sm
matplotlib.use('Cairo')
matplotlib.style.use("fast")
centrimeters = 1/2.54

def change_name(row):
    if row == "Week Before":
        return "2 Weeks Before"
    else:
        return "1 Weeks Before"


def get_data_week_before(kind):
    kind = kind.replace(' ','_').lower()
    with open("data/to_plot/stat_neighbors_users_{kind}.csv".format(kind=kind),"r") as inpuf:
        df = pd.read_csv(inpuf)
    df["at"] = 1/df["at"]
    df["yw_name"] = df.apply(lambda x:change_name(x["yw_name"]),axis = 1)
    return df


def get_data_week(kind):
    kind = kind.replace(' ','_').lower()
    with open("data/to_plot/stat_neighbors_users_{kind}.csv".format(kind=kind),"r") as inpuf:
        df = pd.read_csv(inpuf)
    df["at"] = 1/df["at"]
    return df


def main_w2v(kind,pal,title):
    dict_lim = {"nfl":[(0,100),(4,14)],"nba":[(0,100),(5,15)],"politics":[(0,100),(5,15)],"europe":[(0,100),(3,14)]}
    week_data_df = get_data_week(kind)
    if kind.startswith('E'):
        kind0 = "europe"
    else:
        dict_kinds = {"NBA Trades":"nba","US 2020":"politics","NFL Kickoff Game":"nfl","Brexit":"europe"}
        kind0 = dict_kinds[kind]
    old_data_df = get_data_week_before(kind0)
    old_data_df = old_data_df[old_data_df["yw_name"] == "2 Weeks Before"]
    df = pd.concat([week_data_df,old_data_df])
    df["temp_index"] = 0
    df.loc[df["yw_name"] == "Week Before","temp_index"] = 1
    df.loc[df["yw_name"] == "2 Weeks Before","temp_index"] = 2
    df = df.sort_values(by = ["temp_index"])
    fontsize = 180
    y = 200
    x = 220
    fig = plt.figure(figsize = (x*centrimeters,y*centrimeters))
    ############################
    ax = fig.add_subplot(2,1,1)
    sns.histplot(data = df,ax = ax,
                 stat = "count", x = "value_neighbors",
                 hue = "yw_name",palette = pal,
                 element = "step",fill = False,lw = 0.0,kde = True,line_kws=dict(linewidth=30),
                 log_scale = False,legend =True,
                 )
    #######
    old_legend = ax.legend_
    handles = []
    for x in old_legend.legendHandles:
        x._linewidth = 30
        handles.append(x)
    labels = [t.get_text() for t in old_legend.get_texts()]
    ax.legend(handles = handles, labels = labels,fontsize = fontsize*0.88, loc = "lower center", bbox_to_anchor = (.5, 1),ncol = 3,edgecolor = "grey",markerscale = 2)
    #######
    ax.tick_params(axis='both', which='major', labelsize = 110,size = 80)
    ax.tick_params(axis='both', which='minor', labelsize = 70,size = 50)
    ax.set_xlabel("Neighbourhoods' Characteristic Distance",fontsize = fontsize,labelpad = 30)
    ax.set_ylabel("Count (Users)",fontsize = fontsize,labelpad = 30)
    ax.set_xlim(dict_lim[kind0][1])
    ############################
    ax = fig.add_subplot(2,1,2)
    sns.histplot(data = df,ax = ax,
                 stat = "count", x = "value_user",
                 hue = "yw_name",palette = pal,
                 element = "step",fill = False,lw = 0.0,legend = False,kde = True,line_kws=dict(linewidth=30),
                 )
    #######
    ax.tick_params(axis='both', which='major', labelsize = 110,size = 80)
    ax.tick_params(axis='both', which='minor', labelsize = 70,size = 50)
    ax.set_xlabel("Users' Characteristic Distance",fontsize = fontsize,labelpad = 30)
    ax.set_ylabel("Count (Users)",fontsize = fontsize,labelpad = 30)
    ax.set_xlim(dict_lim[kind0][1])
    #######
    fig.subplots_adjust(top = 0.9, bottom = 0.1,left = 0.09,right = 0.97)
    fig.savefig("fig/users_density/w2v_users_"+kind0+".pdf")


def main_freq(kind,pal,title):
    week_data_df = get_data_week(kind)
    if kind.startswith('E'):
        kind0 = "europe"
    else:
        dict_kinds = {"NBA Trades":"nba","US 2020":"politics","NFL Kickoff Game":"nfl","Brexit":"europe"}
        kind0 = dict_kinds[kind]
    old_data_df = get_data_week_before(kind0)
    old_data_df = old_data_df[old_data_df["yw_name"] == "2 Weeks Before"]
    df = pd.concat([week_data_df,old_data_df])
    df["temp_index"] = 0
    df.loc[df["yw_name"] == "Week Before","temp_index"] = 1
    df.loc[df["yw_name"] == "2 Weeks Before","temp_index"] = 2
    df = df.sort_values(by = ["temp_index"])
    fontsize = 180
    y = 200
    x = 220
    fig = plt.figure(figsize = (x*centrimeters,y*centrimeters))
    ############################
    ax = fig.add_subplot(2,1,1)
    sns.histplot(data = df,ax = ax,
                 stat = "count", x = "at",
                 hue = "yw_name",palette = pal,
                 element = "step",fill = False,lw = 0.0,kde = True,line_kws=dict(linewidth=30),
                 log_scale = True,
                 )
    ####################################################################################
    week1 = df[df["temp_index"] == 2]["at"].tolist()
    week2 = df[df["temp_index"] == 1]["at"].tolist()
    event_week = df[df["temp_index"] == 0]["at"].tolist()
    ks_weekbef = stats.wasserstein_distance(week1,week2)
    ks_week_ev = stats.wasserstein_distance(week2,event_week)
    print("#"*128)
    print(kind)
    print(ks_weekbef)
    print(ks_week_ev)
    ####################################################################################
    old_legend = ax.legend_
    handles = []
    for x in old_legend.legendHandles:
        x._linewidth = 30
        handles.append(x)
    labels = [t.get_text() for t in old_legend.get_texts()]
    ax.legend(handles = handles, labels = labels,fontsize = fontsize*0.88, loc = "lower center", bbox_to_anchor = (.5, 1),ncol = 3,edgecolor = "grey",markerscale = 3)
    #######
    ax.tick_params(axis='both', which='major', labelsize = 110,size = 80)
    ax.tick_params(axis='both', which='minor', labelsize = 70,size = 50)
    ax.set_xlabel("Frequency of Activity",fontsize = fontsize,labelpad = 30)
    ax.set_ylabel("Count (Users)",fontsize = fontsize,labelpad = 30)
    xmin = df.degree.min()
    xmax = df.degree.max()
    ############################
    ax = fig.add_subplot(2,1,2)
    sns.histplot(data = df,ax = ax,
                 stat = "count", x = "degree",
                 hue = "yw_name",palette = pal,
                 element = "step",fill = False,lw = 0.0,kde = True,line_kws=dict(linewidth=30),
                 log_scale = True,legend = False,
                 )
    #######
    #######
    ax.tick_params(axis='both', which='major', labelsize = 110,size = 80)
    ax.tick_params(axis='both', which='minor', labelsize = 70,size = 50)
    ax.set_xlabel("Degree",fontsize = fontsize,labelpad = 30)
    ax.set_ylabel("Count (Users)",fontsize = fontsize,labelpad = 30)
    fig.subplots_adjust(top = 0.9, bottom = 0.1,left = 0.09,right = 0.97)
    fig.savefig("fig/users_density/freq_degree_"+kind0+".pdf")


#
pal = {"NBA Trades":"#DD802F","2 Weeks Before":"#802FDD","Week Before":"#A973E8"}
kind = "NBA Trades"
main_freq(kind,pal,"NBA")
pal = {"US 2020":"#BF000D","2 Weeks Before":"#1C4B8C","Week Before":"#3377D7"}
kind = "US 2020"
main_freq(kind,pal,"U.S. Politics")
pal = {"NFL Kickoff Game":"#FFCE2B","2 Weeks Before":"#4DB6CB","Week Before":"#90D2DF"}
kind = "NFL Kickoff Game"
main_freq(kind,pal,"NFL")
pal = {"US 2020":"#2A8000","2 Weeks Before":"#4D7999","Week Before":"#85A8C1"}
kind = "EUS 2020"
main_freq(kind,pal,"europe")

#
#
pal = {"NBA Trades":"#DD802F","2 Weeks Before":"#802FDD","Week Before":"#A973E8"}
kind = "NBA Trades"
main_w2v(kind,pal,"NBA")
pal = {"US 2020":"#BF000D","2 Weeks Before":"#1C4B8C","Week Before":"#3377D7"}
kind = "US 2020"
main_w2v(kind,pal,"U.S. Politics")
pal = {"NFL Kickoff Game":"#FFCE2B","2 Weeks Before":"#4DB6CB","Week Before":"#90D2DF"}
kind = "NFL Kickoff Game"
main_w2v(kind,pal,"NFL")
pal = {"US 2020":"#2A8000","2 Weeks Before":"#4D7999","Week Before":"#85A8C1"}
kind = "EUS 2020"
main_w2v(kind,pal,"europe")
#