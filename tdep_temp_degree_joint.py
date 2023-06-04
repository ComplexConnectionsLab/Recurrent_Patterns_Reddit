import seaborn as sns
import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Cairo')
matplotlib.style.use("fast")


def plot_data(kind,pal,title,kind0):
    kind = kind.replace(' ','_').lower()
    with open("data/users/users_degree_"+kind0+".json","r") as inpuf:
        data = json.load(inpuf)
    with open("data/to_plot/stat_neighbors_users_{kind}.csv".format(kind=kind),"r") as inpuf:
        df = pd.read_csv(inpuf)
    year_weeks = df["year_week"].unique().tolist()
    yw_names = {row["year_week"]:row["yw_name"] for _,row in df.iterrows()}
    output = []
    for year_week in year_weeks:
        yw_name = yw_names[year_week]
        d = data[year_week]
        #unroll values
        for (user,dict_values) in d.items():
            if dict_values["degree_before"] == 0:
                continue
            if dict_values["knn_before"] == 0:
                continue
            if dict_values["knn_now"] == 0:
                continue
            if dict_values["degree_now"] == 0:
                continue
            x = dict_values["degree_now"]/dict_values["degree_before"]
            y = dict_values["knn_now"]/dict_values["knn_before"]
            output.append({"x":x,"y":y,"yw_name":yw_name})
    df = pd.DataFrame(output)
    fontsize = 96
    fig = plt.figure(figsize = (96,64),dpi = 500)
    g = sns.jointplot(data = df, x = "x",y = "y", hue = "yw_name",
                      height = 40,
                      s = 800,palette = pal,alpha = 0.6)
    ax = g.ax_joint
    ax.set_xlabel(r"$\frac{k(t)}{k(t-1)}$",fontsize = fontsize)
    ax.set_ylabel(r"$\frac{k_{nn}(t)}{k_{nn}(t-1)}$",fontsize = fontsize)
    ax.tick_params(axis='both', which='major', labelsize = 48,size = 32)
    ax.tick_params(axis='both', which='minor', labelsize = 48,size = 32)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles = handles[2:], labels = labels[2:],fontsize = fontsize, loc = 0,ncol = 2,edgecolor = "grey",markerscale = 3)
    ax_marg = g.ax_marg_x
    ax_marg.tick_params(axis='both', which='major', labelsize = 32,size = 16)
    ax_marg.tick_params(axis='both', which='minor', labelsize = 32,size = 16)
    ax_marg.yaxis.set_major_locator(plt.MaxNLocator(3))
    ax_marg = g.ax_marg_y
    ax_marg.tick_params(axis='both', which='major', labelsize = 32,size = 16)
    ax_marg.tick_params(axis='both', which='minor', labelsize = 32,size = 16)
    fig = g.fig
    fig.suptitle(title, fontsize = fontsize)
    fig.tight_layout(rect = (0.0,0.0,1.0,0.98))
    fig.savefig("fig/users_variation/users_degree_joint_"+kind+".pdf")

#
pal = {"NBA Trades":"#DD802F","Week Before":"#802FDD"}
kind = "NBA Trades"
kind0 = "nba"
plot_data(kind,pal,"NBA",kind0)
pal = {"US 2020":"#BF000D","Week Before":"#1C4B8C"}
kind = "US 2020"
kind0 = "politics"
plot_data(kind,pal,"U.S. Politics",kind0)
pal = {"NFL Kickoff Game":"#FFCE2B","Week Before":"#4DB6CB"}
kind = "NFL Kickoff Game"
kind0 = "nfl"
plot_data(kind,pal,"NFL",kind0)
