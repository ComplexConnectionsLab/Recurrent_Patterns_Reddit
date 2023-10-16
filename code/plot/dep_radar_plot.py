import pytz
from datetime import datetime,timedelta
import pandas as pd
import numpy as np
import seaborn as sns
import json
#
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.dates as mdates
matplotlib.use('Cairo')
matplotlib.style.use("fast")
#radar plot fun
def _invert(x, limits):
	"""inverts a value x on a scale from
	limits[0] to limits[1]"""
	return limits[1] - (x - limits[0])

def _scale_data(data, ranges):
	"""scales data[1:] to ranges[0],
	inverts if the scale is reversed"""
	for d, (y1, y2) in zip(data[1:], ranges[1:]):
		assert (y1 <= d <= y2) or (y2 <= d <= y1)
	x1, x2 = ranges[0]
	d = data[0]
	if x1 > x2:
		d = _invert(d, (x1, x2))
		x1, x2 = x2, x1
	sdata = [d]
	for d, (y1, y2) in zip(data[1:], ranges[1:]):
		if y1 > y2:
			d = _invert(d, (y1, y2))
			y1, y2 = y2, y1
		sdata.append((d-y1) / (y2-y1)
					 * (x2 - x1) + x1)
	return sdata

class ComplexRadar():
	def __init__(self, fig, variables, ranges,
				 n_ordinate_levels=7):
		angles = np.arange(0, 360, 360./len(variables))
		axes = [fig.add_axes([0.2, 0.2, 0.6, 0.6],polar=True,label = "axes{}".format(i)) for i in range(len(variables))]
		l, text = axes[0].set_thetagrids(angles, labels = variables,fontsize = 32)
		for txt, angle in zip(text, angles):
			x,y = txt.get_position()
			if txt.get_text() == "Compression":
				txt.set_position((x-0.25,y-0.25))
			elif txt.get_text() == "Skeweness":
				txt.set_position((x-0.25,y-0.25))
			else:
				txt.set_position((x-0.15,y-0.15))
			txt.set_rotation_mode(None)
			txt.set_rotation(angle+30)
		for ax in axes[1:]:
			ax.patch.set_visible(False)
			ax.grid("off")
			ax.xaxis.set_visible(False)
		for i, ax in enumerate(axes):
			grid = np.linspace(*ranges[i],num=n_ordinate_levels)
			if round(ranges[i][0],0) == 0.0:
				gridlabel = ["{}".format(round(x,2)) for x in grid]
			else:
				gridlabel = ["{}".format(int(x)) for x in grid]
			if len(list(set(gridlabel))) != len(gridlabel):
				gridlabel = ["{}".format(round(x,1)) for x in grid]
			if ranges[i][0] > ranges[i][1]:
				grid = grid[::-1] # hack to invert grid
						  # gridlabels aren't reversed
			gridlabel[0] = "" # clean up origin
			ax.set_rgrids(grid, labels=gridlabel, angle=angles[i],fontsize = 20)
			ax.spines["polar"].set_visible(False)
			ax.set_ylim(*ranges[i])

		# variables for plotting
		self.angle = np.deg2rad(np.r_[angles, angles[0]])
		self.ranges = ranges
		self.ax = axes[0]
	def plot(self, data, *args, **kw):
		sdata = _scale_data(data, self.ranges)
		l = self.ax.plot(self.angle, np.r_[sdata, sdata[0]], *args, **kw)
		return l
	def fill(self, data, *args, **kw):
		sdata = _scale_data(data, self.ranges)
		self.ax.fill(self.angle, np.r_[sdata, sdata[0]], *args, **kw)


dict_scales_subreddits = {"nfl":{
								"sentiment":(-4,4),
								"skew_dt":(1.5,4),
								"dtw":(0,900),
								"coherence":(0.12,0.22),
								"compression":(0.2,0.3),
								"bigrams":(0.1,0.7)
						},
						"nba":{
								"sentiment":(-4,4),
								"skew_dt":(1.5,4),
								"dtw":(0,800),
								"coherence":(0.10,0.25),
								"compression":(0.18,0.26),
								"bigrams":(0.2,0.8)
						},
						"politics":{
									"sentiment":(-4,4),
									"skew_dt":(1.5,4),
									"dtw":(100,500),
									"coherence":(0.15,0.3),
									"compression":(0.14,0.22),
									"bigrams":(0.1,0.7)
						},
						"europe":{
								"sentiment":(-4,4),
								"skew_dt":(1.5,4),
								"dtw":(10,50),
								"coherence":(0.10,0.15),
								"compression":(0.2,0.28),
								"bigrams":(0.2,0.8)
						}
					}


'''
def plot_radar_two_shocks(kind,events):
	with open("data/to_plot/radar_"+kind+".csv","r") as inpuf:
		data_df = pd.read_csv(inpuf,sep = ",")
	fig = plt.figure()
	ax = fig.add_subplot(111, projection="polar")
	#1
	df = data_df[data_df["event"] == events[0]]
	# theta has 5 different angles, and the first one repeated
	theta = np.arange(len(df) + 1) / float(len(df)) * 2 * np.pi
	# values has the 5 values from 'Col B', with the first element repeated
	values = df['value'].values
	values = np.append(values, values[0])
	l1, = ax.plot(theta, values, color="C2", marker="o", label="Name of Col B")
	ax.set_xticks(theta[:-1])
	ax.set_xticklabels(df['metric'], color='grey', size=12)
	ax.tick_params(pad=10) # to increase the distance of the labels to the plot
	ax.fill(theta, values, 'green', alpha=0.1)
	#2
	df = data_df[data_df["event"] == events[1]]
	# theta has 5 different angles, and the first one repeated
	theta = np.arange(len(df) + 1) / float(len(df)) * 2 * np.pi
	# values has the 5 values from 'Col B', with the first element repeated
	values = df['value'].values
	values = np.append(values, values[0])
	l1, = ax.plot(theta, values, color="violet", marker="o", label="Name of Col B")
	ax.fill(theta, values, 'violet', alpha=0.1)
	fig.savefig("fig/radar_plot/test.png")
'''
def plot_radar_one_shock(dict_scales_subreddits,kind,event,title,colors):
	#event
	event_label = event
	with open("data/to_plot/radar_"+kind+".csv","r") as inpuf:
		data_df = pd.read_csv(inpuf,sep = ",")
	tmp = data_df[data_df["metric"] == "posts"]
	min_ev = tmp["value"].min()
	max_ev = tmp["value"].max()
	df = data_df[data_df["event"] == event]
	#not event
	with open("data/to_plot/radar_not_events_"+kind+".csv","r") as inpuf:
		data_df = pd.read_csv(inpuf,sep = ",")
	ndf = data_df[data_df["event"] == event]
	tmp = ndf[ndf["metric"] == "posts"]
	min_nev = tmp["value"].min()
	max_nev = tmp["value"].max()
	#scale posts
	dict_scales = dict_scales_subreddits[kind]
	del dict_scales["sentiment"]
	dict_scales["posts"] = (np.min([min_nev,min_ev]),np.max([max_ev,max_nev]))
	#order values and ranges
	metrics = list(dict_scales.keys())
	ranges = [dict_scales[metric] for metric in metrics]
	#rename
	dict_rename = {"sentiment":"Sentiment","skew_dt":"Skeweness","dtw":"DTW","coherence":"Coherence","compression":"Compression","bigrams":"Cosine \n Similarity","posts":"Volume\n Conversations"}
	del dict_rename["sentiment"]
	df = df[df["metric"] != "sentiment"]
	ndf = ndf[ndf["metric"]!="sentiment"]
	metrics = dict_rename.values()
	df["metric"] = df.apply(lambda x: dict_rename[x["metric"]],axis = 1)
	ndf["metric"] = ndf.apply(lambda x: dict_rename[x["metric"]],axis = 1)
	values_ev = [df[df["metric"] == metric]["value"].iloc[0]for metric in metrics]
	values_nev = [ndf[ndf["metric"] == metric]["value"].iloc[0]for metric in metrics]
	#plot
	fig = plt.figure(figsize = (18,18))
	radar = ComplexRadar(fig, metrics, ranges,n_ordinate_levels = len(ranges))
	event, = radar.plot(values_ev,color = colors[0] ,lw = 4)
	nevent, = radar.plot(values_nev,color = colors[1],lw = 4)
	legendax = fig.add_axes([0.8,0.8,0.1,.1])
	legendax.legend(handles = [event,nevent], labels = [event_label,"Week Before"],fontsize = 32, loc = 8, bbox_to_anchor=(0.0,0.05,1,1), bbox_transform=fig.transFigure)
	legendax.axis('off')
	fig.suptitle(title,x = 0.5,y = 0.90, fontsize = 48)
	#
	fig.savefig("fig/radar_plot/"+kind+".png")
	fig.savefig("fig/radar_plot/"+kind+".pdf")
plot_radar_one_shock(dict_scales_subreddits,"nba","NBA Trades","NBA",["#DD802F","#9643DB"])
plot_radar_one_shock(dict_scales_subreddits,"politics","US 2020","U.S. Politics",["#9C2E36","#184072"])

#1F6145
#6F1980
#
#9C2E36
#184072
