import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import random
matplotlib.use('Cairo')
matplotlib.style.use("fast")

def plot_data(kind):
    with open("data/to_plot/semantic_paradox_{kind}.csv".format(kind=kind),"r") as inpuf:
        df = pd.read_csv(inpuf)
    year_weeks = [str(2020) + "_"+str(i) for i in range(1,54)]
    for i in range(1,5):
        year_weeks.append(str(2021) + "_" + str(i))
    list_to_use = random.sample(year_weeks, 5)
    print(list_to_use)
    for l in list_to_use:
        xdf = df[df["year_week"] == l]
        event = xdf["event"].unique()[0]
        is_event = xdf["is_event"].unique()[0]
        fontsize = 120
        fig = plt.figure(figsize = (96,64),dpi = 500)
        g = sns.jointplot(data = xdf,
                          x = "value_user",y = "value_neighbors",
                          height = 64,s = 2000,alpha = 0.6,
                          marginal_ticks = True)
        ax = g.ax_joint
        ax.set_xlabel("Node Compression",fontsize = fontsize)
        ax.set_ylabel("Neighbors' Compression",fontsize = fontsize)
        ax.tick_params(axis='both', which='major', labelsize = 64,size = 48)
        ax.tick_params(axis='both', which='minor', labelsize = 64,size = 48)
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles = handles[2:], labels = labels[2:],fontsize = fontsize, loc = 0,ncol = 2,edgecolor = "grey",markerscale = 3)
        fig = g.fig
        if is_event == "Yes":
            title = event + " Event Week"
        elif is_event == "Week Before":
            title = event + " Week Before"
        else:
            title = "No Event"
        fig.suptitle(title, fontsize = fontsize)
        fig.subplots_adjust(top = 0.95, bottom = 0.07,left = 0.1,right = 0.95)
        fig.savefig("fig/semantic_paradox/"+kind+"_"+l+".pdf")


plot_data("nba")
plot_data("nfl")
plot_data("politics")
plot_data("europe")