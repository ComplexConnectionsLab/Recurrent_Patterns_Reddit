import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import json
import scipy
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.ticker import MaxNLocator
import statsmodels.api as sm
matplotlib.use('Cairo')
matplotlib.style.use("fast")

################################################################
#Frequency-Degree

def change_name(row):
    if row == "Week Before":
        return "2 Weeks Before"
    else:
        return "1 Weeks Before"




def plot_data_time_degree(kind,pal,title):
    dict_lim = {"NBA":[(0.01,10.0),(1,1_000)],"U.S. Politics":[(0.01,10.0),(1,10_000)],"NFL":[(0.01,10.0),(1,1_000)]}
    kind = kind.replace(' ','_').lower()
    with open("data/to_plot/stat_neighbors_users_{kind}.csv".format(kind=kind),"r") as inpuf:
        df = pd.read_csv(inpuf)
    df["at"] = 1/df["at"]
    fontsize = 300
    fig = plt.figure(figsize = (96,64),dpi = 500)
    g = sns.JointGrid(data = df,
                      x = "at", y = "degree",hue = "yw_name",
                      height = 124, palette = pal, space = 0.1,
                      marginal_ticks = True)
    g.plot_joint(sns.scatterplot,
                 s = 6000, alpha =.6, marker = "o")
    g.plot_marginals(sns.ecdfplot,
                     complementary = True,stat = "proportion",
                     lw = 22)
    ax = g.ax_joint
    #fit
    for (event,color) in pal.items():
        tdf = df[df["yw_name"] == event]
        y = np.log(tdf["degree"].tolist())
        X = np.log(tdf["at"].tolist())
        X = sm.add_constant(X)
        model = sm.OLS(y, X)
        results = model.fit()
        Xs = np.linspace(dict_lim[title][0][0]*1.2,dict_lim[title][0][1]*0.8, num = tdf.shape[0])
        xs = np.log(Xs)
        r = results.params
        y = np.exp(r[0]+r[1]*xs)
        ax.plot(Xs, y, lw = 26,color = color)
    ############################
    ax.set_xlabel("Frequency of Activity",fontsize = fontsize,labelpad = 30)
    ax.set_ylabel("Degree",fontsize = fontsize,labelpad = 30)
    ax.tick_params(axis='both', which='major', labelsize = 150,size = 124)
    ax.tick_params(axis='both', which='minor', labelsize = 100,size = 64)
    ax.set_ylim(dict_lim[title][1])
    ax.set_xlim(dict_lim[title][0])
    ax.set_xscale('log',base = 10)
    ax.set_yscale('log',base = 10)
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
    ax_marg.set_xscale('log',base = 10)
    ax_marg.set_yscale('log',base = 10)
    ax_marg.set_ylim(dict_lim[title][1])
    ############################
    fig = g.fig
    fig.suptitle(title, fontsize = fontsize)
    fig.subplots_adjust(top = 0.95, bottom = 0.07,left = 0.1,right = 0.95)
    fig.savefig("fig/supplementary/users_time_degree/users_freq_degree_"+kind+".pdf")


def plot_data_compression(kind,pal,title):
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
    fig.savefig("fig/supplementary/users_compression/users_freq_compression_"+kind+".pdf")


def plot_data_w2v_neigh(kind,pal,title,kind0):
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
                output.append({"x":x,"y":y,"yw_name":yw_name,"user":user})
            except:
                continue
    df = pd.DataFrame(output)
    if kind0 == "nfl":
        df.loc[df["yw_name"] == "NFL Kickoff Game","yw_name"] = "Kickoff Game"
    ux = []
    uy = []
    x = []
    y = []
    xf = []
    yf = []
    #df["x"] = np.log10(df["x"])
    for (user,xdf) in df.groupby(by = ["user"]):
        if xdf.shape[0] == 1:
            continue
        x.append(xdf["x"].iloc[0])
        y.append(xdf["y"].iloc[0])
        ux.append(xdf["x"].iloc[1]-xdf["x"].iloc[0])
        uy.append(xdf["y"].iloc[1]-xdf["y"].iloc[0])
        xf.append(xdf["x"].iloc[1])
        yf.append(xdf["y"].iloc[1])
    xi = np.linspace(np.min(x), np.max(x), int(len(x)))
    yi = np.linspace(np.min(y), np.max(y), int(len(y)))
    X, Y = np.meshgrid(xi, yi)
    U = scipy.interpolate.griddata((x, y), ux, (X, Y), method = 'linear',rescale = True)
    V = scipy.interpolate.griddata((x, y), uy, (X, Y), method = 'linear',rescale = True)
    #
    fontsize = 200
    cmap = ListedColormap([pal[-1],pal[0]], N = 30)
    fig = plt.figure(figsize = (96,64),dpi = 500)
    ax = fig.add_subplot(111)
    '''
    if kind0 == "nba":
        ax.streamplot(X, Y, U, V,
                      linewidth = 10,
                      arrowsize = 12,
                      #color = pal[-1],
                      color = "grey",
                      density = 2,
                      maxlength = 1_000,
                      integration_direction = "forward")
    else:
        ax.streamplot(X, Y, U, V,
                      linewidth = 10,
                      arrowsize = 12,
                      #color = pal[-1],
                      color = "grey",
                      density = 2,
                      maxlength = 10,
                      integration_direction = "forward")
    '''
    ax.tick_params(axis='both', which='major', labelsize = 120,size = 84)
    ax.tick_params(axis='both', which='minor', labelsize = 110,size = 64)
    ax.set_ylabel("Neighbors' Semantic Diversity",fontsize = fontsize,labelpad = 15)
    ax.set_xlabel("Neighbors' Degree",fontsize = fontsize,labelpad = 15)
    ################################################################
    '''
    xmin = np.min(xf)
    xmax = np.max(xf)*0.8
    ymin = np.min(yf)
    ymax = np.max(yf)
    xx, yy = np.mgrid[xmin:xmax:100j, ymin:ymax:100j]
    positions = np.vstack([xx.ravel(), yy.ravel()])
    values = np.vstack([xf, yf])
    kernel = st.gaussian_kde(values)
    f = np.reshape(kernel(positions).T, xx.shape)
    xif = np.linspace(np.min(xf), np.max(xf), int(len(xf)))
    yif = np.linspace(np.min(yf), np.max(yf), int(len(yf)))
    X, Y = np.meshgrid(xif, yif)
    #ax.contour(X, Y, f,linewidths = 15,colors = pal[0])
    '''
    sns.kdeplot(ax = ax, x=x, y=y,
                color = pal[1],
                linewidth = 15,
                levels = 4,
                fill = False,
                thresh = .2)
    sns.kdeplot(ax = ax, x=xf, y=yf,
                #color = pal[1],
                cmap = sns.color_palette("light:"+pal[0], as_cmap=True),
                levels = 5,
                fill = True,
                thresh = .2)
    ################################################################
    #ax.set_xticks(np.log10([20, 60, 140,300,620]))
    #ax.set_xticklabels(["20", "60", "140","300","620"])
    ax.set_xscale("log",base = 10)
    if kind0 == "politics":
        ax.set_xlim([10,1_000])
    else:
        ax.set_xlim([10,3_00])
    ax.set_ylim([6,14])
    fig.suptitle(title, fontsize = fontsize)
    fig.subplots_adjust(top = 0.93, bottom = 0.1,left = 0.1,right = 0.95)
    fig.savefig("fig/supplementary/users_semantic_density/users_neigh_degree_w2v_"+kind+".pdf")




#
pal = {"Orlando":"#DD802F","Week Before":"#802FDD"}
kind = "Orlando"
plot_data_time_degree(kind,pal,"NBA")
pal = {"Capitol Hill":"#BF000D","Week Before":"#1C4B8C"}
kind = "Capitol Hill"
plot_data_time_degree(kind,pal,"U.S. Politics")
pal = {"NFL Kickoff Game":"#FFCE2B","Week Before":"#4DB6CB"}
kind = "NFL Kickoff Game"
plot_data_time_degree(kind,pal,"NFL")
pal = {"NFL Draft":"#FFCE2B","Week Before":"#4DB6CB"}
kind = "NFL Draft"
plot_data_time_degree(kind,pal,"NFL")
#

#
pal = {"Orlando":"#DD802F","Week Before":"#802FDD"}
kind = "Orlando"
plot_data_compression(kind,pal,"NBA")
pal = {"Trump":"#BF000D","Week Before":"#1C4B8C"}
kind = "Trump"
plot_data_compression(kind,pal,"U.S. Politics")
pal = {"NFL Kickoff Game":"#FFCE2B","Week Before":"#4DB6CB"}
kind = "NFL Kickoff Game"
plot_data_compression(kind,pal,"NFL")
pal = {"NFL Draft":"#FFCE2B","Week Before":"#4DB6CB"}
kind = "NFL Draft"
plot_data_compression(kind,pal,"NFL")
#

#
pal = ["#DD802F","#802FDD"]
kind = "Orlando"
kind0 = "nba"
plot_data_w2v_neigh(kind,pal,"NBA",kind0)
pal = ["#BF000D","#1C4B8C"]
kind = "Trump"
kind0 = "politics"
plot_data_w2v_neigh(kind,pal,"U.S. Politics",kind0)
pal = ["#FFCE2B","#4DB6CB"]
kind = "NFL Kickoff Game"
kind0 = "nfl"
plot_data_w2v_neigh(kind,pal,"NFL",kind0)
pal = ["#FFCE2B","#4DB6CB"]
kind = "NFL Draft"
kind0 = "nfl"
plot_data_w2v_neigh(kind,pal,"NFL",kind0)
#
