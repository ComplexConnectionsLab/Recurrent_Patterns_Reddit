import json
import matplotlib.pyplot as plt
import matplotlib
import statsmodels.api as sm
import numpy as np
matplotlib.use('Cairo')
matplotlib.style.use("fast")

centrimeters = 1/2.54


def plot_data():
    subs = ["politics","nba","nfl","europe"]
    x = []
    y = []
    for sub in subs:
        with open("data/ts_interactions/compression_check_"+sub+".json","r") as inpuf:
            data = json.load(inpuf)
        for (k,ls) in data.items():
            for d in ls.values():
                x.append(d[0])
                y.append(d[1])
    X = np.log(x)
    Y = np.log(y)
    X = sm.add_constant(X)
    model = sm.OLS(Y, X)
    results = model.fit()
    print(results.summary())
    ycm = 210
    xcm = 297
    fig = plt.figure(figsize = (xcm*centrimeters,ycm*centrimeters))
    ax = fig.add_subplot(1,1,1)
    ax.scatter(x,y,s = 50)
    ax.tick_params(axis='both', which='major', labelsize = 128,size = 48)
    ax.tick_params(axis='both', which='minor', labelsize = 128,size = 48)
    ax.set_yscale("log")
    ax.set_xscale("log")
    ax.set_xlabel("Compression",fontsize = 240)
    ax.set_ylabel("Length",fontsize = 240)
    fig.savefig("fig/compression_check.pdf")


plot_data()