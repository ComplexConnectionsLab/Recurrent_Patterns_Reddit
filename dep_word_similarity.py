import pandas as pd
import pytz
import json
import seaborn as sns
import numpy as np
from datetime import datetime,timedelta
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle

matplotlib.use('Cairo')
matplotlib.style.use("fast")
centrimeters = 1/2.54
def get_ngrams(kind):
	year_weeks = ["2020_"+str(i) for i in range(1,54)]
	for i in range(1,5):
		year_weeks.append("2021_"+str(i))
	patterns = {}
	tmp_week = {}
	id_pattern = 0
	xs = []
	for year_week in year_weeks:
		with open("data/ngrams/"+kind+"_"+year_week+".csv","r") as inpuf:
			df = pd.read_csv(inpuf)
		z_scores = []
		for _,row in df.iterrows():
			yt = row[[str(y) for y in range(100)]]
			if yt.std() == 0.0:
				continue
			z_score = (row["how_many_times"]-yt.mean())/yt.std()
			z_scores.append({"pattern":row["pattern"],"z_score":z_score})
		z_df = pd.DataFrame(z_scores)
		z_df = z_df.sort_values(by = ["z_score"],ascending = False)
		how_many = int(z_df.shape[0]*0.15)
		z_df = z_df.head(how_many)
		z_scores = {}
		for _,row in z_df.iterrows():
			z_scores[row["pattern"]] = row["z_score"]
			if row["pattern"] not in patterns:
				patterns[row["pattern"]] = id_pattern
				id_pattern +=1
		tmp_week[year_week] = z_scores
		xs.append(datetime.strptime(year_week + '-1', "%Y_%W-%w"))
	#normalize data
	week_data = {}
	for (week,data) in tmp_week.items():
		week_data[week] = np.zeros(id_pattern)
		for (pattern,z_score) in data.items():
			week_data[week][patterns[pattern]] = z_score
		norm = np.linalg.norm(week_data[week])
		week_data[week] = week_data[week]/norm
	tmp = np.array([v for v in week_data.values()])
	pairwise_similarity = tmp.dot(tmp.T)
	output_data = []
	for x in range(0,len(year_weeks)):
		for y in range(0,len(year_weeks)):
			if x == y:
				continue
			output_data.append({"x":xs[x],"y":xs[y],"value":pairwise_similarity[x,y]})
	df = pd.DataFrame(output_data)
	return df


def plot_data(kind,title):
	dict_color = {
		"nfl":"#4DB6CB",
		"politics":"#D94576",
		"nba":"#538F4D",
		"europe":"#855247"
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
	dict_reddit_events = {
		"europe": ["Brexit","Cyprus","Belarus Protest","Lockdown Ease","US 2020","Capitol Hill","Coronavirus"],
		"politics": ["Trump","Trump Covid","US 2020","Capitol Hill","Coronavirus","BLM"],
		"nba":["Kobe Bryant","NBA Stop","NBA Restart","Orlando","NBA Finals","NBA Trades"],
		"nfl":["NFL Draft","NFL Kickoff Game","SuperBowl LIV","NFL Trades","NFL PlayOff"]
	}
	dict_event = {}
	for (k,v) in tmp.items():
		v.replace(tzinfo = utc_tmzone)
		year = v.year
		week = v.isocalendar()[1]
		dict_event[k] = str(year)+"_"+str(week)
	dict_reddit_events = {k:[dict_event[v0] for v0 in v] for (k,v) in dict_reddit_events.items()}
	y = 210*(1/2)
	x = 297*(1/2)
	fig = plt.figure(figsize = (x*centrimeters,y*centrimeters))
	fontsize = 150
	ax_up = fig.add_subplot(1,1,1)
	#pattern / ngrams
	color = dict_color[kind]
	df = get_ngrams(kind)
	df = df.drop_duplicates(subset=["x","y"])
	####################################
	S = 1_00
	df["value"] = pd.cut(df["value"],[i/S for i in range(0,S+1)],labels = [i/S for i in range(0,S)])
	df["value"] = pd.to_numeric(df["value"])
	df["cat"] = df["x"]>df["y"]
	df = df[df["cat"]]
	####################################
	pal = sns.color_palette("light:"+color, as_cmap=True)
	####################################
	g = sns.relplot(data = df, x = "x",y = "y",size = "value",hue = "value",
					size_norm=(0.0, 1.0),hue_norm = (0.0,1.0),
					sizes = (500,6_000),marker = "s",
					palette = pal,alpha = 0.7,
					height = 64, aspect = 64/64)
	g._legend.remove()
	ax_up = g.ax
	fig = g.fig
	ax_up.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
	ax_up.yaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
	ax_up.tick_params(axis='both', which='major', labelsize = 96,size = 64)
	ax_up.tick_params(axis='both', which='minor', labelsize = 96,size = 64)
	#
	fig.suptitle("Word Similarity: "+title, fontsize = fontsize)
	#
	fig.subplots_adjust(top = 0.95, bottom = 0.05,left = 0.15,right = 0.9)
	fig.savefig("fig/word_similarity/"+kind+".pdf")



plot_data("nfl","NFL")
#plot_data("nba","NBA")
#plot_data("europe","Europe")
#plot_data("politics","U.S. Politics")
