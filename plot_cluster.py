import pandas as pd
import pytz
from datetime import datetime,timedelta
import matplotlib.pyplot as plt
import matplotlib
import json
from tqdm import tqdm
import numpy as np
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
matplotlib.use('Cairo')
matplotlib.style.use("fast")

est = pytz.timezone('US/Eastern')
utc_tmzone = pytz.utc
tmp = {
		#us
		"Trump Covid":datetime(2020,10,2),
		"Trump":datetime(2020,2,5),
		"US 2020":datetime(2020,11,3),
		"Capitol Hill":datetime(2021,1,6),
		"BLM":datetime(2020,6,6),
		#covid-19
		"Coronavirus":datetime(2020,3,11),
		"Lockdown Ease":datetime(2020,5,1),
		#eu
		"Brexit":datetime(2020,1,31),
		"Belarus Protest":datetime(2020,8,10),
		"Cyprus":datetime(2020,9,10),
		#March 11 – COVID-19 pandemic: The World Health Organization declares the COVID-19 outbreak a pandemic.[51]
		#nba
		"Orlando":datetime(2020,7,31),
		"NBA Finals":datetime(2020,10,11),
		"NBA Trades":datetime(2020,11,21),
		"Kobe Bryant":datetime(2020,1,26),
		"NBA Stop":datetime(2020,3,12),
		"NBA Restart":datetime(2020,12,22),
		#nfl
		"NFL Draft":datetime(2020,4,24),
		"NFL Kickoff Game":datetime(2020,9,11),
		"NFL PlayOff 2020":datetime(2020,1,5),
		"SuperBowl LIV":datetime(2020,2,2),
		"NFL Trades":datetime(2020,3,18),
		"NFL PlayOff":datetime(2021,1,10),
	}
dict_events = {}
for (k,v) in tmp.items():
	v.replace(tzinfo = utc_tmzone)
	year = v.year
	week = v.isocalendar()[1]
	dict_events[k] = [str(year)+"_"+str(week)]
	v_1 = v-timedelta(days = 7)
	year = v_1.year
	week = v_1.isocalendar()[1]
	if str(year)+"_"+str(week) == "2021_53":
		dict_events[k].append("2020_53")
	else:
		dict_events[k].append(str(year)+"_"+str(week))
dict_reddit_events = {
					"europe": ["Brexit","Cyprus","Belarus Protest","Lockdown Ease","US 2020","Capitol Hill","Coronavirus"],
					"politics": ["Trump","Trump Covid","US 2020","Capitol Hill","Coronavirus","BLM"],
					"nba":["Kobe Bryant","NBA Stop","NBA Restart","Orlando","NBA Finals","NBA Trades"],
					"nfl":["NFL Draft","NFL Kickoff Game","NFL PlayOff 2020","SuperBowl LIV","NFL Trades","NFL PlayOff"]
					}

def change_name(row,ev,inwhat,sub,sub_target):
	if sub == sub_target:
		if row == ev:
			return inwhat
		else:
			return row
	else:
		return row

def get_data():
	year_weeks = ["2020_"+str(i) for i in range(1,54)]
	for i in range(1,5):
		year_weeks.append("2021_"+str(i))
	xs = []
	for kind in ["politics","europe","nba","nfl"]:
		with open("data/users/users_cluster_"+kind+".json","r") as inpuf:
			data = json.load(inpuf)
		for i in range(0,len(year_weeks)):
			t = year_weeks[i]
			users = list(data[t].keys())
			time = datetime.strptime(t + '-1', "%Y_%W-%w")
			for user in users:
				dt = data[t][user]["dt"]/3600
				dr = data[t][user]["w2v"]
				ds = data[t][user]["sentiment"]
				xs.append({"date":time,"yw":t,"w2v":dr,"t":dt,"s":ds,"user":user,"subreddit":kind})
	df = pd.DataFrame(xs)
	return df
'''
dict_reddit_events = {
					"politics": ["US 2020","Capitol Hill"],
					"nba":["Orlando","NBA Trades"],
					"nfl":["NFL Kickoff Game","NFL Draft"],
					}
'''
df = get_data()
df = df.dropna()
N = 4
df["t"] = pd.qcut(df["t"], N, labels=[str(i) for i in range(N)])
events = []
for kind in ["politics","nba","nfl"]:
	for key in dict_reddit_events[kind]:
		ev = dict_events[key][0]
		df["yw"] = df.apply(lambda x:change_name(x["yw"],ev,key,x["subreddit"],kind),axis = 1)
		events.append(key)
events = list(set(events))
df = df[df["yw"].isin(events)]
colors = {"nfl":"#1F6145","nba":"#DD802F","politics":"#9C2E36","europe":"blue"}
fontsize = 48
fig = plt.figure(figsize = (32,32))
ax = fig.add_subplot(1,1,1)
sns.boxplot(data = df, x = "t",hue = "subreddit",y = "w2v",order = [str(i) for i in range(N)],palette = colors,saturation = 0.7,linewidth = 4,dodge = True)
ax.set_xlabel("Percentile of Answering Time [%]",fontsize = fontsize)
ax.set_ylabel("Charateristic Distance",fontsize = fontsize)
ax.tick_params(axis='both', which='major', labelsize = 48,size = 32)
ax.tick_params(axis='both', which='minor', labelsize = 48,size = 32)
ax.legend(fontsize = fontsize, loc = 0,ncol = 2,edgecolor = "grey",markerscale = 3)
ax.set_title("Tell me how you get excited during shocks and \n I’ll tell you what you’re talking about (more or less)",fontsize = 70)
ax.set_xticklabels(["25","50","75","100"])
fig.tight_layout(rect = (0.0,0.0,1.0,0.98))
fig.savefig("fig/test/cluster.png")

'''
#cluster
X =  df[["w2v","t"]].to_numpy()
kmeans = KMeans(n_clusters = 1,random_state = 42,max_iter = 1000,tol = 1e-09)
kmeans.fit(X)
inertia_0 = kmeans.inertia_
inertias = []
silhouettes = []
K = 15
for k in tqdm(range(2,K)):
    kmeans = KMeans(n_clusters = k,random_state = 42,max_iter = 1000,tol = 1e-09)
    kmeans.fit(X)
    inertias.append(kmeans.inertia_/inertia_0)
    preds = kmeans.labels_
    score = silhouette_score(X, preds)
    silhouettes.append(score)
fig = plt.figure(figsize = (12,12))
ax = fig.add_subplot(2,1,1)
ax.plot(range(2,K),inertias,'x-')
ax.set_xlabel('k')
ax.set_ylabel('Inertia')
ax.set_title('The Elbow Method')
ax = fig.add_subplot(2,1,2)
ax.plot(range(2,K),silhouettes,'x-')
ax.set_xlabel('k')
ax.set_ylabel('Silhouette')
ax.set_title('Silhouette Score')
fig.suptitle("K Means")
fig.tight_layout()
fig.savefig("fig/test/kmeans.png")
'''
