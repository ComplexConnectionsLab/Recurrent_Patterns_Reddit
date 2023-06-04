import pandas as pd
import pytz
from datetime import datetime,timedelta
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import matplotlib.dates as mdates
matplotlib.use('Cairo')
matplotlib.style.use("fast")
import seaborn as sns
def plot_data(kind,title):
	dict_color_ev = {"nba":"#9643DB","nfl":"#2A868C","politics":"#184072","europe":"#DBB706"}
	dict_color = {
					"politics":"#9C2E36",
					"nfl":"#1F6145",
					"nba":"#DD802F",
					"europe":"#118AB2",
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
	dict_events_all = {}
	for (k,v) in tmp.items():
		v.replace(tzinfo = utc_tmzone)
		dict_events[k] = v
		v_1 = v+timedelta(days = 4)
		v_2 = v-timedelta(days = 4)
		dict_events_all[k] = [v_1,v_2]
	dict_ev_sp = {"europe":"Lockdown Ease","politics":"Capitol Hill","nba":"Orlando","nfl":"SuperBowl LIV"}
	dict_reddit_events = {
						"europe": ["Brexit","Cyprus","Belarus Protest","Lockdown Ease","US 2020","Capitol Hill","Coronavirus"],
						"politics": ["Trump","Trump Covid","US 2020","Capitol Hill","Coronavirus","BLM"],
						"nba":["Kobe Bryant","NBA Stop","NBA Restart","Orlando","NBA Finals","NBA Trades"],
						"nfl":["NFL Draft","NFL Kickoff Game","NFL PlayOff 2020","SuperBowl LIV","NFL Trades","NFL PlayOff"]
						}

	with open("data/basic_stats/"+kind+".csv","r") as inpuf:
		df = pd.read_csv(inpuf,sep = ";")
	df["tdate"] = df.apply(lambda x: datetime(int(x["date"].split("_")[0]),int(x["date"].split("_")[1]),int(x["date"].split("_")[2])), axis = 1)
	df = df.sort_values(by = ["tdate"])
	df = df.drop_duplicates(subset = ["tdate"])
	N = len(dict_reddit_events[kind])
	yt = np.zeros(7)
	ev = dict_ev_sp[kind]
	dates = dict_events_all[ev]
	tdf = df[(df["tdate"].dt.date>dates[1].date())&(df["tdate"].dt.date<dates[0].date())]
	tdf["posts"] = (tdf["posts"]-tdf["posts"].min())/(tdf["posts"].max()-tdf["posts"].min())
	pls = sns.color_palette("light:"+dict_color_ev[kind], as_cmap = False, n_colors = tdf.shape[0]).as_hex()
	tdf = tdf.sort_values(by = ["posts"])
	tdf["colors"] = pls
	tdf = tdf.sort_values(by = ["tdate"])
	print(tdf)
	print("#"*128)
	for i in range(0,N):
		event = dict_reddit_events[kind][i]
		dates = dict_events_all[event]
		tdf = df[(df["tdate"].dt.date>dates[1].date())&(df["tdate"].dt.date<dates[0].date())]
		tdf["posts"] = (tdf["posts"]-tdf["posts"].min())/(tdf["posts"].max()-tdf["posts"].min())
		y = tdf["posts"].tolist()
		y = np.array(y)
		yt += y/N
	df = pd.DataFrame()
	df["yt"] = yt
	df["range"] = list(range(yt.shape[0]))
	pls = sns.color_palette("light:"+dict_color[kind], as_cmap = False, n_colors = tdf.shape[0]).as_hex()
	df = df.sort_values(by = ["yt"])
	df["colors"] = pls
	df = df.sort_values(by = ["range"])
	print(kind)
	print(df)
	print("#"*128)

plot_data("nba","NBA")
plot_data("politics","U.S. Politics")
plot_data("nfl","NFL")
plot_data("europe","Europe")
