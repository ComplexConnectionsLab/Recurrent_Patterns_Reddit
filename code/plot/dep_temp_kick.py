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
    titles = ["NBA","U.S. Politics","NFL"]
    dict_color = {"NBA":"#DD802F","U.S. Politics":"#BF000D","NFL":"#FFCE2B"}
    output = []
    for (id,kind0) in enumerate(["NBA Trades","US 2020","NFL Kickoff Game"]):
        kind = kind0.replace(' ','_').lower()
        with open("data/w2v_posts/w2v_velocity_gyration_"+kind+".json","r") as outpuf:
            posts = json.load(outpuf)
        with open("data/w2v_posts/w2v_users_posts_"+kind+".json","r") as outpuf:
            users = json.load(outpuf)
        for (post,list_values) in posts.items():
            users_value = np.array(users[post])
            output.append({"type":titles[id],
                           "post_id":post,
                           "velocity":list_values[0],
                           "gyration_post":list_values[1],
                           "gyration_users":np.mean(users_value,axis = 0)[0],
                           "user_activity":np.mean([np.log10(x[1]) for x in users[post]])
                           })
    df = pd.DataFrame(output)
    fontsize = 120
    #
    fig = plt.figure(figsize = (96,64),dpi = 500)
    ax = fig.add_subplot(1,1,1)
    sns.scatterplot(data = df,
                    x = "velocity",y = "gyration_users",
                    size = "user_activity",
                    sizes = (500,5000),
                    palette = dict_color,alpha = 0.6,
                    )
    ax.set_xlabel("Post Displacements",fontsize = fontsize)
    ax.set_ylabel("Users' Charateristic Distance",fontsize = fontsize)
    ax.tick_params(axis='both', which='major', labelsize = 64,size = 48)
    ax.tick_params(axis='both', which='minor', labelsize = 64,size = 48)
    ax.set_ylim([8,12])
    ax.set_xlim([10,20])
    handles, labels = ax.get_legend_handles_labels()
    handles = []
    labels = []
    #ax.legend(handles = handles, labels = labels,fontsize = fontsize, loc = 0,ncol = 2,edgecolor = "grey",markerscale = 3)
    '''
    ################################################################
    output = []
    for (id,kind0) in enumerate(["NBA Trades","US 2020","NFL Kickoff Game"]):
        kind = kind0.replace(' ','_').lower()
        with open("data/time_posts/posts_time_"+kind+".json","r") as outpuf:
            posts = json.load(outpuf)
        with open("data/w2v_posts/w2v_users_posts_"+kind+".json","r") as outpuf:
            users = json.load(outpuf)
        for (post,list_values) in posts.items():
            users_value = np.array([x[1] for x in users[post]])
            output.append({"type":titles[id],
                           "post_id":post,
                           "distance_to_parent":g_mean(list_values[0]),
                           "distance_to_post":g_mean(list_values[1]),
                           "activity_users":g_mean(users_value),
                           })
    df = pd.DataFrame(output)
    #
    ax = fig.add_subplot(1,2,2)
    sns.scatterplot(data = df,
                    x = "distance_to_post",y = "activity_users",
                    s = 4500,
                    palette = dict_color,alpha = 0.6,
                    )
    ax.set_xlabel("Distance to Post",fontsize = fontsize)
    ax.set_ylabel("Users' Activty",fontsize = fontsize)
    ax.tick_params(axis='both', which='major', labelsize = 64,size = 48)
    ax.tick_params(axis='both', which='minor', labelsize = 64,size = 48)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles = handles, labels = labels,fontsize = fontsize, loc = 0,ncol = 2,edgecolor = "grey",markerscale = 3)
    #
    '''
    fig.subplots_adjust(top = 0.95, bottom = 0.07,left = 0.1,right = 0.95)
    fig.savefig("fig/test.pdf")



plot_data()