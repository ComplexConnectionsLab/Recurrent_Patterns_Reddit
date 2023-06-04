import pandas as pd
import pytz
import json
import seaborn as sns
from scipy.stats import zscore
import numpy as np
from datetime import datetime,timedelta
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.dates as mdates
matplotlib.use('Cairo')
matplotlib.style.use("fast")
def plot_data(kind,title):
	dict_color = {
					"nfl":["#C09B7C","#2A868C"],
					"politics":["#184072","#E06790"],
					"nba":["#BC87E8","#75B06F"],
					"europe":["#6F1980","#FFD90F"]
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
			"SuperBowl LIV":datetime(2020,2,2),
			"NFL Trades":datetime(2020,3,18),
			"NFL PlayOff":datetime(2021,1,10),
		}
	dict_events = {}
	for (k,v) in tmp.items():
		v.replace(tzinfo = utc_tmzone)
		dict_events[k] = v
	dict_reddit_events = {
						"europe": ["Brexit","Cyprus","Belarus Protest","Lockdown Ease","US 2020","Capitol Hill","Coronavirus"],
						"politics": ["Trump","Trump Covid","US 2020","Capitol Hill","Coronavirus","BLM"],
						"nba":["Kobe Bryant","NBA Stop","NBA Restart","Orlando","NBA Finals","NBA Trades"],
						"nfl":["NFL Draft","NFL Kickoff Game","SuperBowl LIV","NFL Trades","NFL PlayOff"]
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
	ax = fig.add_subplot(1,1,1)
	with open("data/distribution/sentiment_"+kind+".json","r") as inpuf:
		data = json.load(inpuf)
	year_weeks = ["2020_"+str(i) for i in range(1,54)]
	for i in range(1,5):
		year_weeks.append("2021_"+str(i))
	dict_yw = {year_week:id for (id,year_week) in enumerate(year_weeks)}
	t_data = []
	for year_week in year_weeks:
		d = data[year_week]
		d = np.array(d)
		mask = d != 0.0
		d = d[mask]
		hist,bin_edges = np.histogram(d,bins = 20)
		xbin = (bin_edges[1:]+bin_edges[:-1])/2
		t_data.append(hist)
	zs = zscore(t_data, axis = None)
	ls = ["solid","dashed"]
	t_plot = {0:[],1:[]}
	for event in dict_reddit_events[kind]:
		for id,week in enumerate(dict_events[event]):
			id_z = dict_yw[week]
			z = zs[id_z]
			t_plot[id].append(z)
	dict_plot = {k:np.mean(v,axis = 0) for (k,v) in t_plot.items()}
	labels = ["Event","Week Before"]
	color_other = "#ABACB0"
	lws = [4,2]
	for (k,v) in t_plot.items():
		for x in v:
			ax.plot(xbin,x,lw = lws[k],ls = ls[k],color = color_other)
	for (k,v) in dict_plot.items():
		color = dict_color[kind][k]
		ax.plot(xbin,v,lw = 16,ls = ls[k],color = color,label = labels[k])
	ax.set_ylabel("Z-score",fontsize = fontsize)
	ax.set_xlabel("Sentiment",fontsize = fontsize)
	ax.tick_params(axis='both', which='major', labelsize = 48,size = 32)
	ax.tick_params(axis='both', which='minor', labelsize = 48,size = 32)
	ax.legend(fontsize = fontsize, loc = 0,ncol = 2,edgecolor = "grey")
	fig.suptitle(title, fontsize = fontsize)
	#
	fig.tight_layout(rect = (0.0,0.0,1.0,0.98))
	fig.savefig("fig/distrib_sentiment/"+kind+".png")
	fig.savefig("fig/distrib_sentiment/"+kind+".pdf")

plot_data("nba","NBA")
plot_data("politics","U.S. Politics")
plot_data("europe","Europe")
plot_data("nfl","NFL")
