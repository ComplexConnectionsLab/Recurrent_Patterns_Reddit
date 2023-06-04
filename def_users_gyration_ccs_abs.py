import pandas as pd
import pytz
from datetime import datetime,timedelta
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.dates as mdates
import json
import numpy as np
from scipy.spatial import distance
import seaborn as sns
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
'''
#boh rick
def get_event(row,dict_events):
	for (event,weeks) in dict_events.items():
		if row == weeks[0]:
			return "Event"
		elif row == weeks[1]:
			return "Week Before"
	return "Remove"
def get_user_w2v(kind):
	year_weeks = ["2020_"+str(i) for i in range(1,54)]
	for i in range(1,5):
		year_weeks.append("2021_"+str(i))
	with open("data/users/users_gyration_w2v_"+kind+".json","r") as inpuf:
		data = json.load(inpuf)
	xs = []
	user_dt = {}
	for i in range(0,len(year_weeks)):
		t = year_weeks[i]
		users = list(data[t].keys())
		time = datetime.strptime(t + '-1', "%Y_%W-%w")
		for user in users:
			dt = np.mean(data[t][user]["dt"])/3600
			dr = data[t][user]["w2v"]
			if user not in user_dt:
				user_dt[user] = [[],[]]
			user_dt[user][0].append(dr)
			user_dt[user][1].append(dt)
	newdata = {k:[np.abs(np.diff(v[0])),v[1][1:]] for (k,v) in user_dt.items()}
	for (user,diff_data) in newdata.items():
		for i in range(len(diff_data[0])):
			t = year_weeks[i+1]
			time = datetime.strptime(t + '-1', "%Y_%W-%w")
			xs.append({"time":time,"yw":t,"m":diff_data[0][i],"dt":diff_data[1][i],"user":user})
	df = pd.DataFrame(xs)
	return df
df = get_user_w2v("nba")
df = df.sort_values(by = ["time"])
df["event"] = df.apply(lambda x:get_event(x["yw"],dict_events),axis = 1)
df = df[df["event"] != "Remove"]
df = df.sort_values(by = ["time"])
df["dt"] = pd.qcut(df["dt"], 10, labels=[str(i) for i in range(10)])
fontsize = 40
fig = plt.figure(figsize = (48,32))
ax = fig.add_subplot(1,1,1)
palette = sns.color_palette("crest",10)
sns.set_theme(style = "whitegrid")
sns.boxplot(data = df, x = "dt",hue = "event",y = "m",order = [str(i) for i in range(10)])
#sns.stripplot(data = df,jitter = 0.8,dodge = True,x = "m",y = "yw",hue = "dt",ax = ax,palette = palette,marker = "8",s = 30,linewidth = 1, alpha = 0.7)
ax.legend(fontsize = fontsize, loc = 0,ncol = 2,edgecolor = "grey",markerscale = 3)
ax.set_xlabel("Quantile DT",fontsize = fontsize)
ax.set_ylabel("Radius of Gyration",fontsize = fontsize)
ax.tick_params(axis='both', which='major', labelsize = 48,size = 32)
ax.tick_params(axis='both', which='minor', labelsize = 48,size = 32)
fig.savefig("fig/test.png")
'''
def change_name(row,ev,inwhat):
	if row == ev[0]:
		return inwhat
	else:
		return "Week Before"
#old super cute data
def get_user_w2v(kind):
	year_weeks = ["2020_"+str(i) for i in range(1,54)]
	for i in range(1,5):
		year_weeks.append("2021_"+str(i))
	with open("data/users/users_gyration_w2v_"+kind+".json","r") as inpuf:
		data = json.load(inpuf)
	xs = []
	for i in range(0,len(year_weeks)):
		t = year_weeks[i]
		users = list(data[t].keys())
		time = datetime.strptime(t + '-1', "%Y_%W-%w")
		for user in users:
			dt = np.mean(data[t][user]["dt"])/3600
			dr = data[t][user]["w2v"]
			xs.append({"time":time,"yw":t,"m":dr,"dt":dt,"user":user})
	df = pd.DataFrame(xs)
	return df

#politics
kind = "politics"
df = get_user_w2v("politics")
df = df.sort_values(by = ["time"])
ev = dict_events["US 2020"]
N = 4
df["dt"] = pd.qcut(df["dt"], N, labels=[str(i) for i in range(N)])
df = df[df["yw"].isin(ev)]
df["yw"] = df.apply(lambda x:change_name(x["yw"],ev,"US 2020"),axis = 1)
pal = {"US 2020":"#9C2E36","Week Before":"#184072"}
pal2 = {"US 2020":"#CB4D56","Week Before":"#225DAA"}
fontsize = 72
fig = plt.figure(figsize = (48,32))
ax = fig.add_subplot(1,1,1)
sns.boxplot(data = df, x = "dt",hue = "yw",y = "m",order = [str(i) for i in range(N)],palette = pal,saturation = 0.7,linewidth = 4,dodge = True)
sns.swarmplot(data = df, x = "dt",hue = "yw",y = "m",order = [str(i) for i in range(N)],palette = pal2,dodge = True,size = 12,lw = 10,marker = "D")
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles = handles[2:], labels = labels[2:],fontsize = fontsize, loc = 0,ncol = 2,edgecolor = "grey",markerscale = 3)
ax.set_xlabel("Percentile of Answering Time [%]",fontsize = fontsize)
ax.set_ylabel("Charateristic Distance",fontsize = fontsize)
ax.tick_params(axis='both', which='major', labelsize = 48,size = 32)
ax.tick_params(axis='both', which='minor', labelsize = 48,size = 32)
ax.set_xticklabels(["25","50","75","100"])
fig.suptitle("U.S. Politics", fontsize = fontsize)
fig.tight_layout(rect = (0.0,0.0,1.0,0.98))
fig.savefig("fig/radar_plot/"+kind+"_q.png")
fig.savefig("fig/radar_plot/"+kind+"_q.pdf")
#nba
kind = "nba"
df = get_user_w2v("nba")
df = df.sort_values(by = ["time"])
ev = dict_events["NBA Trades"]
N = 4
df["dt"] = pd.qcut(df["dt"], N, labels=[str(i) for i in range(N)])
df = df[df["yw"].isin(ev)]
df["yw"] = df.apply(lambda x:change_name(x["yw"],ev,"NBA Trades"),axis = 1)
pal = {"NBA Trades":"#DD802F","Week Before":"#9643DB"}
pal2 = {"NBA Trades":"#E6A267","Week Before":"#BC87E8"}
fontsize = 72
fig = plt.figure(figsize = (48,32))
ax = fig.add_subplot(1,1,1)
sns.boxplot(data = df, x = "dt",hue = "yw",y = "m",order = [str(i) for i in range(N)],palette = pal,saturation = 0.7,linewidth = 4,dodge = True)
sns.swarmplot(data = df, x = "dt",hue = "yw",y = "m",order = [str(i) for i in range(N)],palette = pal2,dodge = True,size = 12,lw = 10,marker = "D")
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles = handles[2:], labels = labels[2:],fontsize = fontsize, loc = 0,ncol = 2,edgecolor = "grey",markerscale = 3)
ax.set_xlabel("Percentile of Answering Time [%]",fontsize = fontsize)
ax.set_ylabel("Charateristic Distance",fontsize = fontsize)
ax.tick_params(axis='both', which='major', labelsize = 48,size = 32)
ax.tick_params(axis='both', which='minor', labelsize = 48,size = 32)
ax.set_xticklabels(["25","50","75","100"])
fig.suptitle("NBA", fontsize = fontsize)
fig.tight_layout(rect = (0.0,0.0,1.0,0.98))
fig.savefig("fig/radar_plot/"+kind+"_q.png")
fig.savefig("fig/radar_plot/"+kind+"_q.pdf")
