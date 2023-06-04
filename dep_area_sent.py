from scipy.integrate import simpson
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
import matplotlib.lines as mlines
matplotlib.use('Cairo')
matplotlib.style.use("fast")
centrimeters = 1/2.54

def plot_data():
	dict_color_dark = {"NFL":"#E0AC00","U.S. Politics":"#990A13","NBA":"#A65F21","Europe":"#226600"}
	dict_color_light = {"NFL":"#FFDE70","U.S. Politics":"#E53844","NBA":"#E6A267","Europe":"#00A336"}
	dict_color_med = {"NFL":"#FFCE2B","U.S. Politics":"#BF000D","NBA":"#DD802F","Europe":"#2A8000"}
	dict_color = {
					"politics":[["#9C2E36","#CB4D56"],["#184072","#225DAA","#002552"],["#E481A2","#EDABBF","#E06790"]],
					"nfl":[["#1F6145","#3B946F"],["#B8845F","#C09B7C","#855535"],["#2A868C","#52B5BC","#326367"]],
					"nba":[["#DD802F","#E6A267"],["#9643DB","#BC87E8","#6D21AB"],["#75B06F","#9ECB9A","#538F4D"]],
					"europe":[["#118AB2","#2BADD9"],["#6F1980","#A92BC2","#4E0B5C"],["#FFD90F","#FAE370","#DBB706"]],
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
							"europe":["Brexit","Cyprus","Belarus Protest","Lockdown Ease","US 2020","Capitol Hill","Coronavirus"],
							"politics":["Trump","Trump Covid","US 2020","Capitol Hill","Coronavirus","BLM"],
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
	year_weeks = ["2020_"+str(i) for i in range(1,54)]
	for i in range(1,5):
		year_weeks.append("2021_"+str(i))
	dict_yw = {year_week:id for (id,year_week) in enumerate(year_weeks)}
	tmp_yw = {year_week: [year_weeks[i],year_weeks[i-1]] for (i,year_week) in enumerate(year_weeks)}
	tmp_yw.pop("2020_1")
	dict_reddit_not_events = {"europe":{},"politics":{},"nba":{},"nfl":{}}
	for (subreddit,events) in dict_reddit_events.items():
		yws_not_event = tmp_yw.copy()
		for event in events:
			yws_event = dict_events[event][0]
			yws_not_event.pop(yws_event)
		dict_reddit_not_events[subreddit] = yws_not_event
	#
	dict_label = {"europe":"Europe","politics":"U.S. Politics","nfl":"NFL","nba":"NBA"}
	data_to_plot = []
	for id_kind,kind in enumerate(["europe","nba","nfl","politics"]):
		with open("data/distribution/sentiment_"+kind+".json","r") as inpuf:
			data = json.load(inpuf)
		#z-score
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
		for event in dict_reddit_events[kind]:
			integrals = []
			for id,week in enumerate(dict_events[event]):
				id_z = dict_yw[week]
				z = zs[id_z]
				I = simpson(z, xbin)
				integrals.append(I)
			data_to_plot.append({"kind":dict_label[kind],"value":integrals[0]-integrals[1],"is_event":"Yes","event_name":event})
		stats_not_event = []
		for (event,evs) in dict_reddit_not_events[kind].items():
			integrals = []
			for ev in evs:
				id_z = dict_yw[ev]
				z = zs[id_z]
				I = simpson(z, xbin)
				integrals.append(I)
			data_to_plot.append({"kind":dict_label[kind],"value":integrals[0]-integrals[1],"is_event":"No","event_name":event})
	y = 150
	x = 200
	fig = plt.figure(figsize = (x*centrimeters,y*centrimeters))
	fontsize = 140
	ax = fig.add_subplot(1,1,1)
	df = pd.DataFrame(data_to_plot)
	df.to_csv("data/to_plot/area_sentiment.csv",index = False,sep = ",")
	tdf = df[df["is_event"] == "No"]
	order =  ["NFL","NBA","U.S. Politics","Europe"]
	sns.boxplot(order = order,x = "kind",y = "value",data = tdf,ax = ax, palette = dict_color_light,saturation = 0.4,showfliers = False,width = .42)
	sns.swarmplot(x = "kind",order = order, y = "value", data = tdf, palette = dict_color_dark, s = 30,alpha = 0.6)
	df = df[df["is_event"] == "Yes"]
	sns.swarmplot(x = "kind",order = order, y = "value",hue = "kind", data = df, palette = dict_color_med, s = 100,alpha = 1.0,marker = "^")
	#
	nfl = mlines.Line2D([], [], color=dict_color_light["NFL"], marker='^', linestyle='None',markersize=10, label='NFL')
	nba = mlines.Line2D([], [], color=dict_color_light["NBA"], marker='^', linestyle='None',markersize=10, label='NBA')
	pol = mlines.Line2D([], [], color=dict_color_light["U.S. Politics"], marker='^', linestyle='None',markersize=10, label='U.S. Politics')
	eu = mlines.Line2D([], [], color=dict_color_light["Europe"], marker='^', linestyle='None',markersize=10, label='Europe')
	handles=[nfl,nba,pol,eu]
	#
	ax.set_ylabel("Tone Variation",fontsize = fontsize,labelpad = -45)
	ax.set_xlabel("Subreddit",fontsize = fontsize)
	ax.legend(handles = handles,fontsize = fontsize*0.8, title = "Exogenous Events",title_fontsize = fontsize*0.8,loc = 0,ncol = 2,markerscale = 5,edgecolor = "grey")
	ax.tick_params(axis='both', which='major', labelsize = 100,size = 64)
	ax.tick_params(axis='both', which='minor', labelsize = 100,size = 64)
	#
	fig.subplots_adjust(top = 0.95, bottom = 0.07,left = 0.05,right = 0.95)
	fig.savefig("fig/distrib_sentiment/all.pdf")


plot_data()


#Sentiment -> Bin Z-score -> Integral -> Variation of Integral