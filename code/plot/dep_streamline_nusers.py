import seaborn as sns
import pandas as pd
import json
import scipy
import scipy.stats as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.colors import ListedColormap
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
    fig.savefig("fig/streamline/users_neigh_degree_w2v_"+kind+".pdf")



pal = ["#DD802F","#802FDD"]
kind = "NBA Trades"
kind0 = "nba"
plot_data(kind,pal,"NBA",kind0)
pal = ["#BF000D","#1C4B8C"]
kind = "US 2020"
kind0 = "politics"
plot_data(kind,pal,"U.S. Politics",kind0)
pal = ["#FFCE2B","#4DB6CB"]
kind = "NFL Kickoff Game"
kind0 = "nfl"
plot_data(kind,pal,"NFL",kind0)