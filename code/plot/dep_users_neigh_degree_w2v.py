import seaborn as sns
import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.ticker import MaxNLocator
matplotlib.use('Cairo')
matplotlib.style.use("fast")

def plot_data(kind,pal,title,kind0):
    kind = kind.replace(' ','_').lower()
    with open("data/to_plot/stat_neighbors_users_{kind}.csv".format(kind=kind),"r") as inpuf:
        df = pd.read_csv(inpuf)
    with open("data/users/users_degree_"+kind0+".json","r") as inpuf:
        data = json.load(inpuf)
    year_weeks = df["year_week"].unique().tolist()
    yw_names = {row["year_week"]:row["yw_name"] for _,row in df.iterrows()}
    output = []
    for year_week in year_weeks:
        yw_name = yw_names[year_week]
        d = data[year_week]
        #unroll values
        for (user,dict_values) in d.items():
            x = dict_values["knn_now"]
            try:
                y = df[(df["user"] == user) & (df["yw_name"] == yw_name)]["value_neighbors"].iloc[0]
                output.append({"x":x,"y":y,"yw_name":yw_name})
            except:
                continue
    df = pd.DataFrame(output)
    if kind0 == "nfl":
        df.loc[df["yw_name"] == "NFL Kickoff Game","yw_name"] = "Kickoff Game"
    fontsize = 200
    fig = plt.figure(figsize = (96,64),dpi = 500)
    '''
    g = sns.jointplot(data = df,
                      x = "x",y = "y", hue = "yw_name",
                      height = 64,s = 3000,palette = pal,alpha = 0.6,marker = "s",
                      marginal_ticks = True,marginal_kws=dict(fill=False,lw = 18))
    '''
    g = sns.JointGrid(data = df,
                      x = "x", y = "y",hue = "yw_name",
                      height = 124, palette = pal,
                      marginal_ticks = True)
    g.plot_joint(sns.scatterplot,
                 s = 7000, alpha =.6, marker = "s")
    g.plot_marginals(sns.ecdfplot,
                     complementary = True,stat = "proportion",
                     lw = 22)
    ############################
    ax = g.ax_joint
    ax.set_ylabel("Neighbors' Charateristic Distance",fontsize = fontsize,labelpad = 15)
    ax.set_xlabel("Neighbors' Degree",fontsize = fontsize,labelpad = 15)
    ax.tick_params(axis='both', which='major', labelsize = 120,size = 84)
    ax.tick_params(axis='both', which='minor', labelsize = 110,size = 64)
    ax.set_xscale('log',base = 10)
    ax.set_xlim([10,1_000])
    #######
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles = handles[2:], labels = labels[2:],fontsize = fontsize, loc = 0,ncol = 2,edgecolor = "grey",markerscale = 10)
    ############################
    ax_marg = g.ax_marg_x
    ax_marg.tick_params(axis='both', which='major', labelsize = 72,size = 54)
    ax_marg.tick_params(axis='both', which='minor', labelsize = 72,size = 32)
    ax_marg.set_xscale("log",base = 10)
    ax.set_xlim([10,1_000])
    ############################
    ax_marg = g.ax_marg_y
    ax_marg.tick_params(axis='both', which='major', labelsize = 72,size = 54)
    ax_marg.tick_params(axis='both', which='minor', labelsize = 72,size = 32)
    ############################
    fig = g.fig
    fig.suptitle(title, fontsize = fontsize)
    fig.subplots_adjust(top = 0.95, bottom = 0.07,left = 0.1,right = 0.95)
    fig.savefig("fig/neigh_w2v/users_neigh_degree_w2v_"+kind+".pdf")


pal = {"NBA Trades":"#DD802F","Week Before":"#802FDD"}
kind = "NBA Trades"
kind0 = "nba"
plot_data(kind,pal,"NBA",kind0)
pal = {"US 2020":"#BF000D","Week Before":"#1C4B8C"}
kind = "US 2020"
kind0 = "politics"
plot_data(kind,pal,"U.S. Politics",kind0)
pal = {"Kickoff Game":"#FFCE2B","Week Before":"#4DB6CB"}
kind = "NFL Kickoff Game"
kind0 = "nfl"
plot_data(kind,pal,"NFL",kind0)
