import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import json
matplotlib.use('Cairo')
matplotlib.style.use("fast")
def g_mean(x):
    a = np.log10(x)
    return a.mean()



def plot_data():
    dict_event_kind = {"NBA Trades":"NBA",
                       "NBA Restart":"NBA",
                       "Orlando":"NBA",
                       "US 2020":"U.S. Politics",
                       "Trump":"U.S. Politics",
                       "Capitol Hill":"U.S. Politics",
                       "NFL Kickoff Game":"NFL",
                       "SuperBowl LIV":"NFL",
                       "NFL Draft":"NFL",
                       "EBrexit":"Europe",
                       "ECapitol Hill":"Europe",
                       "EUS 2020":"Europe",
                       }
    dict_color = {"NBA":"#DD802F","U.S. Politics":"#BF000D","NFL":"#FFCE2B","Europe":"#2A8000"}
    output = []
    for (kind0,type) in dict_event_kind.items():
        kind = kind0.replace(' ','_').lower()
        with open("data/w2v_posts/w2v_velocity_gyration_"+kind+".json","r") as outpuf:
            posts = json.load(outpuf)
        with open("data/w2v_posts/w2v_users_posts_"+kind+".json","r") as outpuf:
            users = json.load(outpuf)
        for (post,list_values) in posts.items():
            try:
                users_value = np.array(users[post])
                output.append({"type":type,
                               "post_id":post,
                               "velocity":list_values[0],
                               "gyration_post":list_values[1],
                               "gyration_users":np.mean(users_value,axis = 0)[0],
                               "user_activity":np.mean([np.log10(x[1]) for x in users[post]])
                               })
            except:
                print(kind0,type)
                print(users_value)
                continue

    df = pd.DataFrame(output)
    fontsize = 120
    #
    fig = plt.figure(figsize = (96,64),dpi = 500)
    ax = fig.add_subplot(1,1,1)
    sns.scatterplot(data = df,
                    x = "velocity",y = "gyration_users",
                    hue = "type",
                    s = 2_500,
                    palette = dict_color,alpha = 0.6,
                    )
    ax.set_xlabel("Post Displacements",fontsize = fontsize)
    ax.set_ylabel("Users' Charateristic Distance",fontsize = fontsize)
    ax.tick_params(axis='both', which='major', labelsize = 64,size = 48)
    ax.tick_params(axis='both', which='minor', labelsize = 64,size = 48)
    ax.set_ylim([6,12])
    ax.set_xlim([8,20])
    handles, labels = ax.get_legend_handles_labels()
    handles = []
    labels = []
    ax.legend(handles = handles, labels = labels,fontsize = fontsize, loc = 0,ncol = 2,edgecolor = "grey",markerscale = 3)
    fig.subplots_adjust(top = 0.95, bottom = 0.07,left = 0.1,right = 0.95)
    fig.savefig("fig/supplementary/displacement.pdf")



plot_data()