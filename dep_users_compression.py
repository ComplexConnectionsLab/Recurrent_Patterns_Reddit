import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from matplotlib.ticker import MaxNLocator
import statsmodels.api as sm
matplotlib.use('Cairo')
matplotlib.style.use("fast")

def change_name(row):
    if row == "Week Before":
        return "2 Weeks Before"
    else:
        return "1 Weeks Before"


def plot_data_week_before(kind,pal,title):
    dict_lim = {"NBA":[(0.01,10.0),(1,1_000)],"U.S. Politics":[(0.01,10.0),(1,10_000)],"NFL":[(0.01,10.0),(1,1_000)]}
    kind = kind.replace(' ','_').lower()
    with open("data/to_plot/stat_neighbors_users_{kind}.csv".format(kind=kind),"r") as inpuf:
        df = pd.read_csv(inpuf)
    df["at"] = 1/df["at"]
    df["yw_name"] = df.apply(lambda x:change_name(x["yw_name"]),axis = 1)
    fontsize = 180
    fig = plt.figure(figsize = (96,64),dpi = 500)
    g = sns.JointGrid(data = df,
                      x = "at", y = "compression",hue = "yw_name",
                      height = 124, palette = pal, space = 0.3,
                      marginal_ticks = True)
    g.plot_joint(sns.scatterplot,
                 s = 6000, alpha =.6, marker = "s")
    g.plot_marginals(sns.ecdfplot,
                     complementary = True,stat = "proportion",
                     lw = 22)
    ax = g.ax_joint
    ############################
    ax.set_xlabel("Frequency of Activity",fontsize = fontsize,labelpad = 30)
    ax.set_ylabel("Compression",fontsize = fontsize,labelpad = 30)
    ax.tick_params(axis='both', which='major', labelsize = 112,size = 84)
    ax.tick_params(axis='both', which='minor', labelsize = 112,size = 64)
    #ax.set_ylim(dict_lim[title][1])
    ax.set_xlim(dict_lim[title][0])
    ax.set_xscale('log',base = 10)
    #ax.set_yscale('log',base = 10)
    #######
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles = handles[2:], labels = labels[2:],fontsize = fontsize, loc = 0,ncol = 2,edgecolor = "grey",markerscale = 10)
    ############################
    ax_marg = g.ax_marg_x
    ax_marg.tick_params(axis='both', which='major', labelsize = 72,size = 54)
    ax_marg.tick_params(axis='both', which='minor', labelsize = 72,size = 32)
    ax_marg.yaxis.set_major_locator(MaxNLocator(3))
    ax_marg.set_xscale('log',base = 10)
    ax_marg.set_yscale('log',base = 10)
    ax_marg.set_xlim(dict_lim[title][0])
    ############################
    '''
    ax_marg = g.ax_marg_y
    ax_marg.tick_params(axis='both', which='major', labelsize = 72,size = 54)
    ax_marg.tick_params(axis='both', which='minor', labelsize = 72,size = 32)
    ax_marg.xaxis.set_major_locator(MaxNLocator(3))
    ax_marg.set_xscale('log',base = 10)
    ax_marg.set_yscale('log',base = 10)
    ax_marg.set_ylim(dict_lim[title][1])
    '''
    ############################
    fig = g.fig
    fig.suptitle(title, fontsize = fontsize)
    fig.subplots_adjust(top = 0.95, bottom = 0.07,left = 0.1,right = 0.95)
    fig.savefig("fig/users_compression/users_freq_compression_"+kind+".pdf")


def plot_data(kind,pal,title):
    dict_lim = {"NBA":[(0.01,10.0),(1,1_000)],"U.S. Politics":[(0.01,10.0),(1,10_000)],"NFL":[(0.01,10.0),(1,1_000)]}
    kind = kind.replace(' ','_').lower()
    with open("data/to_plot/stat_neighbors_users_{kind}.csv".format(kind=kind),"r") as inpuf:
        df = pd.read_csv(inpuf)
    df["at"] = 1/df["at"]
    fontsize = 300
    fig = plt.figure(figsize = (96,64),dpi = 500)
    g = sns.JointGrid(data = df,
                      x = "at", y = "compression",hue = "yw_name",
                      height = 124, palette = pal, space = 0.1,
                      marginal_ticks = True)
    g.plot_joint(sns.scatterplot,
                 s = 6000, alpha =.6, marker = "s")
    g.plot_marginals(sns.ecdfplot,
                     complementary = True,stat = "proportion",
                     lw = 22)
    ax = g.ax_joint
    ############################
    ax.set_xlabel("Frequency of Activity",fontsize = fontsize,labelpad = 30)
    ax.set_ylabel("Compression",fontsize = fontsize,labelpad = 30)
    ax.tick_params(axis='both', which='major', labelsize = 150,size = 124)
    ax.tick_params(axis='both', which='minor', labelsize = 100,size = 64)
    #ax.set_ylim(dict_lim[title][1])
    ax.set_xlim(dict_lim[title][0])
    ax.set_xscale('log',base = 10)
    #ax.set_yscale('log',base = 10)
    #######
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles = handles[2:], labels = labels[2:],fontsize = fontsize*0.8, loc = 0,ncol = 2,edgecolor = "grey",markerscale = 10)
    ############################
    ax_marg = g.ax_marg_x
    ax_marg.tick_params(axis='both', which='major', labelsize = 72,size = 54)
    ax_marg.tick_params(axis='both', which='minor', labelsize = 72,size = 32)
    ax_marg.yaxis.set_major_locator(MaxNLocator(3))
    ax_marg.set_xscale('log',base = 10)
    ax_marg.set_yscale('log',base = 10)
    ax_marg.set_xlim(dict_lim[title][0])
    ############################
    ax_marg = g.ax_marg_y
    ax_marg.tick_params(axis='both', which='major', labelsize = 72,size = 54)
    ax_marg.tick_params(axis='both', which='minor', labelsize = 72,size = 32)
    ax_marg.xaxis.set_major_locator(MaxNLocator(3))
    ############################
    fig = g.fig
    fig.suptitle(title, fontsize = fontsize)
    fig.subplots_adjust(top = 0.95, bottom = 0.07,left = 0.1,right = 0.95)
    fig.savefig("fig/users_compression/users_freq_compression_"+kind+".pdf")


#
pal = {"NBA Trades":"#DD802F","Week Before":"#802FDD"}
kind = "NBA Trades"
plot_data(kind,pal,"NBA")
pal = {"US 2020":"#BF000D","Week Before":"#1C4B8C"}
kind = "US 2020"
plot_data(kind,pal,"U.S. Politics")
pal = {"NFL Kickoff Game":"#FFCE2B","Week Before":"#4DB6CB"}
kind = "NFL Kickoff Game"
plot_data(kind,pal,"NFL")
#
pal = {"1 Weeks Before":"#DD802F","2 Weeks Before":"#802FDD"}
kind = "nba"
plot_data_week_before(kind,pal,"NBA")
pal = {"1 Weeks Before":"#BF000D","2 Weeks Before":"#1C4B8C"}
kind = "politics"
plot_data_week_before(kind,pal,"U.S. Politics")
pal = {"1 Weeks Before":"#FFCE2B","2 Weeks Before":"#4DB6CB"}
kind = "nfl"
plot_data_week_before(kind,pal,"NFL")