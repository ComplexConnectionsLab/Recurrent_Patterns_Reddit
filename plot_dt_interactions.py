import pandas as pd
import json
import numpy as np
from datetime import datetime,timedelta
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.dates as mdates
matplotlib.style.use("ggplot")
def plot_data(kind,title):
	dict_events = {
					"Trump":datetime(2020,2,5),
					"US 2020":datetime(2020,11,3),
					"Capitol Hill":datetime(2021,1,6),
					"Coronavirus":datetime(2020,3,1),
					"Kobe Bryant":datetime(2020,1,26),
					"GME":datetime(2021,1,25),
					"Pfizer":datetime(2020,11,9),
					"Maradona":datetime(2020,11,25),
					"Market Crash":datetime(2020,3,9),
					"BLM":datetime(2020,5,25),
					"Orlando":datetime(2020,7,31),
					"NBA Finals":datetime(2020,10,11),
					"NBA Trades":datetime(2020,11,21),
					"CL Finals":datetime(2020,8,23),
					"Premier Restart":datetime(2020,6,20),
					"GME Q3":datetime(2020,12,8)
				}
	dict_reddit_events = {
						"europe": ["Trump","US 2020","Capitol Hill","Coronavirus"],
						"politics": ["Trump","US 2020","Capitol Hill","Coronavirus","BLM"],
						"science":["Coronavirus","Pfizer"],
						"cryptocurrency":["Market Crash","GME"],
						"stocks":["Market Crash","GME","Pfizer"],
						"nba":["Kobe Bryant","Orlando","NBA Finals","NBA Trades"],
						"sports":["Kobe Bryant","Maradona"],
						"soccer":["Maradona","CL Finals","Coronavirus","Premier Restart"],
						"wsb":["GME","GME Q3"],
						"nfl":[],
						"ukpolitics":[]
						}
	with open("data/distribution/interactions_"+kind+".json","r") as inpuf:
		data = json.load(inpuf)
	fig = plt.figure(figsize = (32,16))
	ndata = []
	for (k,ls) in data.items():
		ys = np.array(ls)
		ys = ys/3600
		r = datetime.strptime(k + '-1', "%Y_%W-%w")
		std = np.std(ys)/np.sqrt(len(ys))
		m = np.mean(ys)
		m = 1/np.std(ys)
		ndata.append({
					"date":r,
					"mean":m,
					"upper":m+std,
					"lower":m-std
					})
	fontsize = 48
	df = pd.DataFrame(ndata)
	df = df.sort_values(by = ["date"])
	ax = fig.add_subplot(1,1,1)
	ax.plot(df["date"],df["mean"],lw = 6,c = "rosybrown")
	ax.set_ylabel("Δt Interactions [min]",fontsize = fontsize)
	ax.set_xlabel("Date",fontsize = fontsize)
	ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
	ax.tick_params(axis='both', which='major', labelsize = 32,size = 20)
	ax.tick_params(axis='both', which='minor', labelsize = 32,size = 20)
	_, yup = ax.get_ylim()
	#add vertical line
	for event in dict_reddit_events[kind]:
		d = dict_events[event]
		ax.axvline(d, c = "orange", lw = 6)
		ax.text(d,yup,event,verticalalignment='center',fontsize = fontsize)
	fig.suptitle(title, fontsize = fontsize)
	#
	fig.tight_layout(rect = (0.0,0.0,1.0,0.98))
	fig.savefig("fig/dt_interactions_"+kind+".png")
plot_data("ukpolitics","UK Politics")
plot_data("nfl","NFL")
plot_data("politics","US Politics")
plot_data("nba","NBA")
'''
plot_data("politics","US Politics")
plot_data("soccer","Soccer")
plot_data("sports","Sports")
plot_data("nba","NBA")
plot_data("cryptocurrency","Cryptocurrency")
plot_data("europe","Europe")
plot_data("science","Science")
plot_data("stocks","Stocks")
'''
