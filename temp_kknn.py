import seaborn as sns
import pandas as pd
from tqdm import tqdm
import json
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Cairo')
matplotlib.style.use("fast")


def plot_data(kind,pal,title,kind0):
    kind = kind.replace(' ','_').lower()
    with open("data/to_plot/stat_neighbors_users_{kind}.csv".format(kind=kind),"r") as inpuf:
        df = pd.read_csv(inpuf)
    year_weeks = df["year_week"].unique().tolist()
    yw_names = {row["year_week"]:row["yw_name"] for _,row in df.iterrows()}
    output = []
    for year_week in year_weeks:
        graph = nx.read_gpickle("data/network/network_user_{kind}_{year_week}.gpickle".format(kind = kind0,year_week = year_week))
        yw_name = yw_names[year_week]
        for node in tqdm(graph.nodes(),total = graph.number_of_nodes()):
            x = graph.degree(node)
            y = nx.average_neighbor_degree(graph,nodes =[node])[node]
            output.append({"x":x,"y":y,"yw_name":yw_name})
    df = pd.DataFrame(output)
    for k in pal.keys():
        color = pal[k]
        tdf = df[df["yw_name"] == k]
        fontsize = 96
        fig = plt.figure(figsize = (96,64),dpi = 500)
        g = sns.jointplot(data = tdf,
                          x = "x",y = "y",
                          height = 40,s = 800,alpha = 0.6,color = color,
                          marginal_ticks = True)
        ax = g.ax_joint
        ax.set_xlabel("Degree",fontsize = fontsize)
        ax.set_ylabel("Neighbors' Degree",fontsize = fontsize)
        ax.tick_params(axis='both', which='major', labelsize = 48,size = 32)
        ax.tick_params(axis='both', which='minor', labelsize = 48,size = 32)
        ax.set_xscale('log',base = 10)
        ax.set_yscale('log',base = 10)
        ax_marg = g.ax_marg_x
        ax_marg.tick_params(axis='both', which='major', labelsize = 32,size = 16)
        ax_marg.tick_params(axis='both', which='minor', labelsize = 32,size = 16)
        ax_marg.set_xscale("log",base = 10)
        ax_marg.yaxis.set_major_locator(plt.MaxNLocator(3))
        ax_marg = g.ax_marg_y
        ax_marg.tick_params(axis='both', which='major', labelsize = 32,size = 16)
        ax_marg.tick_params(axis='both', which='minor', labelsize = 32,size = 16)
        ax_marg.set_yscale("log",base = 10)
        fig = g.fig
        fig.suptitle(title, fontsize = fontsize)
        fig.tight_layout(rect = (0.0,0.0,1.0,0.98))
        fig.savefig("fig/users_variation/kknn_"+kind+k+".pdf")


#
pal = {"NFL Kickoff Game":"#FFCE2B","Week Before":"#4DB6CB"}
kind = "NFL Kickoff Game"
kind0 = "nfl"
plot_data(kind,pal,"NFL",kind0)
pal = {"NBA Trades":"#DD802F","Week Before":"#802FDD"}
kind = "NBA Trades"
kind0 = "nba"
plot_data(kind,pal,"NBA",kind0)
pal = {"US 2020":"#BF000D","Week Before":"#1C4B8C"}
kind = "US 2020"
kind0 = "politics"
plot_data(kind,pal,"U.S. Politics",kind0)
