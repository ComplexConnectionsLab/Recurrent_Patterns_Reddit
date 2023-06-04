import pandas as pd
import pytz
from datetime import datetime,timedelta
from scipy.stats import skew
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.dates as mdates
import json
import numpy as np
import seaborn as sns
matplotlib.use('Cairo')
matplotlib.style.use("fast")
centrimeters = 1/2.54


def plot_data_time_metrics():
	dict_title = {"nfl":"NFL","nba":"NBA","politics":"U.S. Politics","europe":"Europe"}
	dict_limits = {
		"nfl":[(1.5,4),(0,900),(0.12,0.22)],
		"nba":[(1.5,4),(0,800),(0.10,0.25)],
		"politics":[(1.5,4.5),(100,500),(0.15,0.3)],
		"europe":[(2,4),(10,50),(0.10,0.15)]
	}
	kinds = ["politics","nba","nfl","europe"]
	dict_color = {
		"politics":["#BF000D","#E53844","#990A13"],
		"nfl":["#FFCE2B","#FFDE70","#E0AC00"],
		"nba":["#DD802F","#E6A267","#A65F21"],
		"europe":["#2A8000","#00A336","#226600"],
	}
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
		dict_events[k] = v
	dict_reddit_events = {
		"europe":["Brexit","Cyprus","Belarus Protest","Lockdown Ease","US 2020","Capitol Hill","Coronavirus"],
		"politics":["Trump","Trump Covid","US 2020","Capitol Hill","Coronavirus","BLM"],
		"nba":["Kobe Bryant","NBA Stop","NBA Restart","Orlando","NBA Finals","NBA Trades"],
		"nfl":["NFL Draft","NFL Kickoff Game","NFL PlayOff 2020","SuperBowl LIV","NFL Trades","NFL PlayOff"]
	}
	y = 210*(2/3)
	x = 297*(1/3)
	fig = plt.figure(figsize = (x*centrimeters,y*centrimeters))
	fontsize = 70
	for id,kind in enumerate(kinds):
		color = dict_color[kind][0]
		ax = fig.add_subplot(4,1,id+1)
		with open("data/distribution/interactions_"+kind+".json","r") as inpuf:
			data = json.load(inpuf)
		ndata = []
		for (k,ls) in data.items():
			ys = np.array(ls)
			ys = ys/3600
			r = datetime.strptime(k + '-1', "%Y_%W-%w")
			m = np.mean(ys)
			ndata.append({
				"date":r,
				"y":m,
			})
		df = pd.DataFrame(ndata)
		df = df.sort_values(by = ["date"])
		df = df.drop_duplicates(subset = ["date"])
		ax.scatter(df["date"],df["y"],s = 3500,alpha = 0.7,c = color)
		ax.set_ylabel("μ(Δt)",fontsize = fontsize,labelpad = 40)
		ax.tick_params(axis='both', which='major', labelsize = 64,size = 48)
		ax.tick_params(axis='both', which='minor', labelsize = 64,size = 48)
		ax.set_ylim(dict_limits[kind][0])
		if kind == "europe":
			ax.set_xlabel("Date",fontsize = fontsize,labelpad = 32)
			ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
			ax.set_ylabel("μ(Δt)",fontsize = fontsize,labelpad = 80-5)
		if kind != "europe":
			ax.set_xticklabels([])
		#add vertical line
		ylow, yup = ax.get_ylim()
		for event in dict_reddit_events[kind]:
			d = dict_events[event]
			ax.axvline(d,ymin = 0.05,ymax = 0.87, c = "#585B6E", lw = 10,ls = "dashdot")
		#ax.text(d,yup,event,verticalalignment='center',fontsize = fontsize)
		ax.set_title(dict_title[kind], fontsize = fontsize)
	#
	fig.subplots_adjust(hspace=0.2,top = 0.95,left = 0.2,right = 0.8)
	fig.tight_layout(rect = (0.05,0.05,0.95,0.95))
	fig.savefig("fig/supplementary/average.pdf")

plot_data_time_metrics()

def plot_data(kind,title,event):
	dict_color = {
					"politics":["#9C2E36","#CB4D56","#732226"],
					"nfl":["#1F6145","#3B946F","#10402C"],
					"nba":["#DD802F","#E6A267","#A65F21"],
					"europe":["#118AB2","#2BADD9","#0E6481"],
				}
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
	dict_reddit_events = {
						"europe":["Brexit","Cyprus","Belarus Protest","Lockdown Ease","US 2020","Capitol Hill","Coronavirus"],
						"politics":["Trump","Trump Covid","US 2020","Capitol Hill","Coronavirus","BLM"],
						"nba":["Kobe Bryant","NBA Stop","NBA Restart","Orlando","NBA Finals","NBA Trades"],
						"nfl":["NFL Draft","NFL Kickoff Game","NFL PlayOff 2020","SuperBowl LIV","NFL Trades","NFL PlayOff"]
						}

	dict_event = {}
	dict_events = {}
	for (k,v) in tmp.items():
		v.replace(tzinfo = utc_tmzone)
		year = v.year
		week = v.isocalendar()[1]
		dict_events[k] = [str(year)+"_"+str(week)]
		dict_event[k] = v
		v_1 = v-timedelta(days = 7)
		year = v_1.year
		week = v_1.isocalendar()[1]
		if str(year)+"_"+str(week) == "2021_53":
			dict_events[k].append("2020_53")
		else:
			dict_events[k].append(str(year)+"_"+str(week))
	fig = plt.figure(figsize = (48,32))
	fontsize = 80
	#
	ax = fig.add_subplot(1,1,1)
	ls = ["solid","dashed"]
	with open("data/distribution/interactions_"+kind+".json","r") as inpuf:
		data = json.load(inpuf)
	labels = ["Event","Week Before"]
	for id,w in enumerate(dict_events[event]):
		d = data[w]
		d = np.array(d)
		d = d+0.00000000001
		d = d/3600
		color = dict_color[kind][id]
		#sns.histplot(data = d,ax = ax, element = "poly", stat = "density", fill = False,lw = 16, color = color,ls = ls[id],label = labels[id])
		sns.ecdfplot(ax = ax,data = d,color = color,linewidth = 16,complementary = False,stat = "proportion",ls = ls[id],label = labels[id])
	ax.set_xlim((0.0,15))
	ax.set_ylabel("Cumulative Distribution",fontsize = fontsize)
	ax.set_xlabel("Δt[hour]",fontsize = fontsize)
	ax.tick_params(axis='both', which='major', labelsize = 48,size = 32)
	ax.tick_params(axis='both', which='minor', labelsize = 48,size = 32)
	ax.legend(fontsize = fontsize, loc = 4,ncol = 2,edgecolor = "grey")
	fig.suptitle(title + ": " + event, fontsize = fontsize)
	#
	fig.tight_layout(rect = (0.0,0.0,1.0,0.98))
	#
	if kind == "europe":
		event_chosen_string = "e"+event.replace(" ", "_").lower()
	else:
		event_chosen_string = event.replace(" ", "_").lower()
	fig.savefig("fig/supplementary/distrib_dt/"+event_chosen_string+".pdf")


plot_data("nba","NBA","NBA Trades")
plot_data("nba","NBA","NBA Restart")
plot_data("nba","NBA","NBA Finals")
plot_data("nba","NBA","Orlando")
plot_data("politics","U.S. Politics","BLM")
plot_data("politics","U.S. Politics","US 2020")
plot_data("politics","U.S. Politics","Capitol Hill")
plot_data("politics","U.S. Politics","Trump")
plot_data("nfl","NFL","SuperBowl LIV")
plot_data("nfl","NFL","NFL Kickoff Game")
plot_data("nfl","NFL","NFL Draft")
plot_data("europe","Europe","US 2020")
plot_data("europe","Europe","Brexit")
plot_data("europe","Europe","Capitol Hill")