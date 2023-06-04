import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Cairo')
matplotlib.style.use("fast")


def change_name(row):
    if row == "Week Before":
        return "2 Weeks Before"
    else:
        return "1 Weeks Before"


def plot_data_week_before(kind,pal,title):
    dict_lim = {"nba":[2,14],"nfl":[4,14],"politics":[2,16]}
    kind = kind.replace(' ','_').lower()
    with open("data/to_plot/stat_neighbors_users_{kind}.csv".format(kind=kind),"r") as inpuf:
        df = pd.read_csv(inpuf)
    df["yw_name"] = df.apply(lambda x:change_name(x["yw_name"]),axis = 1)
    fontsize = 120
    fig = plt.figure(figsize = (96,64),dpi = 500)
    g = sns.jointplot(data = df,
                      x = "value_user",y = "value_neighbors", hue = "yw_name",
                      height = 64,s = 2000,palette = pal,alpha = 0.6,
                      marginal_ticks = True)
    ax = g.ax_joint
    ax.set_xlabel("Node Charateristic Distance",fontsize = fontsize)
    ax.set_ylabel("Neighbors' Charateristic Distance",fontsize = fontsize)
    ax.tick_params(axis='both', which='major', labelsize = 64,size = 48)
    ax.tick_params(axis='both', which='minor', labelsize = 64,size = 48)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles = handles[2:], labels = labels[2:],fontsize = fontsize, loc = 0,ncol = 2,edgecolor = "grey",markerscale = 3)
    ax.set_xlim(dict_lim[kind])
    ax_marg = g.ax_marg_x
    ax_marg.tick_params(axis='both', which='major', labelsize = 48,size = 32)
    ax_marg.tick_params(axis='both', which='minor', labelsize = 48,size = 32)
    ax_marg.yaxis.set_major_locator(plt.MaxNLocator(3))
    ax_marg.set_xlim(dict_lim[kind])
    ax_marg = g.ax_marg_y
    ax_marg.tick_params(axis='both', which='major', labelsize = 48,size = 32)
    ax_marg.tick_params(axis='both', which='minor', labelsize = 48,size = 32)
    fig = g.fig
    fig.suptitle(title, fontsize = fontsize)
    fig.subplots_adjust(top = 0.95, bottom = 0.07,left = 0.1,right = 0.95)
    fig.savefig("fig/neigh_w2v/users_w2v_"+kind+".pdf")


def plot_data(kind,pal,title):
    kind = kind.replace(' ','_').lower()
    with open("data/to_plot/stat_neighbors_users_{kind}.csv".format(kind=kind),"r") as inpuf:
        df = pd.read_csv(inpuf)
    fontsize = 120
    fig = plt.figure(figsize = (96,64),dpi = 500)
    g = sns.jointplot(data = df,
                      x = "value_user",y = "value_neighbors", hue = "yw_name",
                      height = 64,s = 2000,palette = pal,alpha = 0.6,
                      marginal_ticks = True)
    ax = g.ax_joint
    ax.set_xlabel("Node Charateristic Distance",fontsize = fontsize)
    ax.set_ylabel("Neighbors' Charateristic Distance",fontsize = fontsize)
    ax.tick_params(axis='both', which='major', labelsize = 64,size = 48)
    ax.tick_params(axis='both', which='minor', labelsize = 64,size = 48)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles = handles[2:], labels = labels[2:],fontsize = fontsize, loc = 0,ncol = 2,edgecolor = "grey",markerscale = 3)
    ax_marg = g.ax_marg_x
    ax_marg.tick_params(axis='both', which='major', labelsize = 48,size = 32)
    ax_marg.tick_params(axis='both', which='minor', labelsize = 48,size = 32)
    ax_marg.yaxis.set_major_locator(plt.MaxNLocator(3))
    ax_marg = g.ax_marg_y
    ax_marg.tick_params(axis='both', which='major', labelsize = 48,size = 32)
    ax_marg.tick_params(axis='both', which='minor', labelsize = 48,size = 32)
    fig = g.fig
    fig.suptitle(title, fontsize = fontsize)
    fig.subplots_adjust(top = 0.95, bottom = 0.07,left = 0.1,right = 0.95)
    fig.savefig("fig/neigh_w2v/users_w2v_"+kind+".pdf")

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