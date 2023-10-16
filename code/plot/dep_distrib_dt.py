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
def plot_data(kind,title,events):
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
	for event in events:
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
	ax.set_xlabel("Δt[min]",fontsize = fontsize)
	ax.tick_params(axis='both', which='major', labelsize = 48,size = 32)
	ax.tick_params(axis='both', which='minor', labelsize = 48,size = 32)
	ax.legend(fontsize = fontsize, loc = 4,ncol = 2,edgecolor = "grey")
	fig.suptitle(title + ": " + events[0], fontsize = fontsize)
	#
	fig.tight_layout(rect = (0.0,0.0,1.0,0.98))
	fig.savefig("fig/distrib_dt/"+kind+".png")
	fig.savefig("fig/distrib_dt/"+kind+".pdf")

plot_data("nba","NBA",["NBA Finals"])
plot_data("politics","U.S. Politics",["Capitol Hill"])
plot_data("nfl","NFL",["SuperBowl LIV"])
plot_data("europe","Europe",["US 2020"])
