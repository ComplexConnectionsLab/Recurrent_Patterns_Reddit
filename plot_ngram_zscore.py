import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime
import matplotlib.dates as mdates
matplotlib.style.use("ggplot")
def plot_data_cosine(kind,title):
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
	ts = [pairwise_similarity[x-1,x] for x in range(1, len(year_weeks))]
	xs = xs[1:]
	fontsize = 48
	fig = plt.figure(figsize = (32,24))
	ax = fig.add_subplot(1,1,1)
	ax.plot(xs,ts,lw = 6, c = "skyblue")
	ax.set_ylabel("Cosine Bigrams",fontsize = fontsize)
	ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
	ax.set_xlabel("Week",fontsize = 20)
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
	fig.savefig("fig/ngrams_cs_"+kind+".png")


def jaccard_sim(list_x,list_y):
	set_x = set(list_x)
	set_y = set(list_y)
	nominator = set_x.intersection(set_y)
	denominator = set_x.union(set_y)
	return len(nominator)/len(denominator)
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
	year_weeks = ["2020_"+str(i) for i in range(1,54)]
	for i in range(1,5):
		year_weeks.append("2021_"+str(i))
	tmp_week = {}
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
		tmp_week[year_week] = [row["pattern"] for _,row in z_df.iterrows()]
		xs.append(datetime.strptime(year_week + '-1', "%Y_%W-%w"))
	pairwise_similarity = np.zeros((len(year_weeks),len(year_weeks)))
	for x,year_week_x in enumerate(year_weeks):
		for y,year_week_y in enumerate(year_weeks):
			jsim_value = jaccard_sim(tmp_week[year_week_x],tmp_week[year_week_y])
			pairwise_similarity[x,y] = jsim_value
	ts = [pairwise_similarity[x-1,x] for x in range(1, len(year_weeks))]
	xs = xs[1:]
	fig = plt.figure(figsize = (32,24))
	ax = fig.add_subplot(1,1,1)
	ax.plot(xs,ts,lw = 4, c = "skyblue")
	ax.set_xlabel("Jaccard",fontsize = 20)
	ax.set_ylabel("Week",fontsize = 20)
	ax.tick_params(axis='both', which='major', labelsize = 20,size = 20)
	ax.tick_params(axis='both', which='minor', labelsize = 20,size = 20)
	_, yup = ax.get_ylim()
	#add vertical line
	for event in dict_reddit_events[kind]:
		d = dict_events[event]
		ax.axvline(d, c = "orange", lw = 4)
		ax.text(d,yup,event,verticalalignment='center',fontsize = 20)
	fig.suptitle(title, y = 0.98, fontsize = 32)
	fig.tight_layout()
	fig.savefig("fig/ngrams_"+kind+".png")
plot_data_cosine("nfl","NFL")
plot_data("nfl","NFL")
plot_data("nba","NBA")
plot_data("politics","US Politics")
plot_data("europe","Europe")
