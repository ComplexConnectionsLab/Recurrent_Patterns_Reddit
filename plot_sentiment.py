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

	with open("data/distribution/sentiment_"+kind+".json","r") as inpuf:
		data = json.load(inpuf)
	fig = plt.figure(figsize = (48,30))
	ndata = []
	for (k,ls) in data.items():
		ys = np.array(ls)
		mask = ys > 0.0
		positive = ys[mask]
		mask = ys < 0.0
		negative = -ys[mask]
		r = datetime.strptime(k + '-1', "%Y_%W-%w")
		ndata.append({
					"date":r,
					"p_count":positive.shape[0],
					"n_count":negative.shape[0],
					"p_mean":np.mean(positive),
					"n_mean":np.mean(negative)
					})
	fontsize = 48
	df = pd.DataFrame(ndata)
	df["p_area"] = df["p_count"]*df["p_mean"]
	df["n_area"] = df["n_count"]*df["n_mean"]
	df = df.sort_values(by = ["date"])
	df["spread"] = (df["p_count"]-df["n_count"])/(df["p_count"]+df["n_count"])
	df["diff"] = df["p_area"]+df["n_area"]
	ax = fig.add_subplot(1,1,1)
	ax.plot(df["date"],df["diff"],lw = 6,c = "deeppink")
	ax.set_ylabel("Sentiment",fontsize = fontsize)
	ax.set_xlabel("Date",fontsize = fontsize)
	ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
	ax.tick_params(axis='both', which='major', labelsize = 32,size = 24)
	ax.tick_params(axis='both', which='minor', labelsize = 32,size = 24)
	_, yup = ax.get_ylim()
	#add vertical line
	for event in dict_reddit_events[kind]:
		d = dict_events[event]
		ax.axvline(d, c = "orange", lw = 6)
		ax.text(d,yup,event,verticalalignment='center',fontsize = fontsize)
	fig.suptitle(title, fontsize = fontsize)
	#
	fig.tight_layout(rect = (0.0,0.0,1.0,0.98))
	fig.savefig("fig/sentiment_"+kind+".png")
plot_data("ukpolitics","UK Politics")
plot_data("nfl","NFL")
