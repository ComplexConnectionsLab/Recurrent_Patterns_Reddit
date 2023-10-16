import pandas as pd
import pytz
from datetime import datetime,timedelta
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.dates as mdates
matplotlib.use('Cairo')
matplotlib.style.use("fast")
centrimeters = 1/2.54
def plot_data(kind,title):
	dict_color = {
					"politics":"#BF000D",
					"nfl":"#FFCE2B",
					"nba":"#DD802F",
					"europe":"#2A8000",
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
	for col in ["posts","comments","leaves","fist_time_users","last_time_users","posts_per_author","comments_per_author"]:
		df[col] = df[col].rolling(7).mean()
	reddit = df[["tdate","posts"]]
	if kind not in ["nba","nfl"]:
		y = 210*(1/3)
		x = 297*(2/3)
		fig = plt.figure(figsize = (x*centrimeters,y*centrimeters))
		ax_posts = fig.add_subplot(1,1,1)
		tax = ax_posts.twinx()
		axes = [ax_posts,tax]
	else:
		y = 210*(1/3)
		x = 297*(2/3)
		fig = plt.figure(figsize = (x*centrimeters,y*centrimeters))
		ax_posts = fig.add_subplot(1,1,1)
		axes = [ax_posts]
	fontsize = 112
	color = dict_color[kind]
	#
	line_post = ax_posts.plot(df["tdate"],df["posts"],lw = 20, c = color, ls = "solid",label = "Posts")
	ax_posts.set_ylabel("Posts",fontsize = fontsize)
	if kind in ["nba","nfl"]:
		ax_posts.set_xlabel("Date",fontsize = fontsize)
	#
	if kind not in ["nba","nfl"]:
		line_comments = tax.plot(df["tdate"],df["comments"],lw = 16,c = color, ls = "dashed",label = "Comments")
		tax.set_ylabel("Comments",fontsize = fontsize,rotation = 270,labelpad = 95)
	#
	for ax in axes:
		ax.tick_params(axis='both', which='major', labelsize = 64,size = 48)
		ax.tick_params(axis='both', which='minor', labelsize = 64,size = 48)
		ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
		#add vertical line
		ylow, yup = ax.get_ylim()
		if kind == "wsb":
			ax.set_yscale("log")
		if (kind in ["nba","nfl"]) and (ax == ax_posts):
			continue
		if ax != tax:
			for event in dict_reddit_events[kind]:
				d = dict_events[event]
				ax.axvline(d,ymin = 0.05,ymax = 0.87, c = "#585B6E", lw = 16,ls = "dashdot")
				#ax.text(d,yup,event,verticalalignment='center',fontsize = fontsize)
	#gtrends
	if kind in ["nba","nfl"]:
		tax = ax_posts.twinx()
		with open("data/gtrends_"+kind+".csv","r") as inpuf:
			df = pd.read_csv(inpuf, sep = ",")
		df["date"] = pd.to_datetime(df["date"],format = "%Y-%m-%d")
		df[kind] = df[kind].rolling(7).mean()
		gtrends = df[["date",kind]].dropna().reset_index()
		reddit = reddit.dropna().reset_index()
		xdf = pd.merge(gtrends,reddit,left_on = "date",right_on = "tdate")
		corr = xdf[kind].corr(xdf["posts"])
		print(kind)
		print(corr)
		line_tax = tax.plot(df["date"],df[kind],c = "#818288",lw = 18,ls = "dotted",label = "Google Trends")
		tax.set_ylabel("Google Trends", fontsize = fontsize, rotation = 270,labelpad = 95)
		tax.tick_params(axis='both', which='major', labelsize = 64,size = 48)
		tax.tick_params(axis='both', which='minor', labelsize = 64,size = 48)
		tax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
		tax.set_ylim([0,100])
		lns = line_tax + line_post
		labs = [l.get_label() for l in lns]
		ax_posts.legend(lns, labs,fontsize = fontsize*0.7, loc = 0,ncol = 2,edgecolor = "grey")
	else:
		lns = line_comments + line_post
		labs = [l.get_label() for l in lns]
		ax_posts.legend(lns, labs,fontsize = fontsize*0.7, loc = 0,ncol = 2,edgecolor = "grey")
	fig.suptitle(title, fontsize = fontsize)
	#
	fig.subplots_adjust(hspace=0.1,top = 0.88)
	fig.savefig("fig/volume/"+kind+".pdf",bbox_inches='tight')

plot_data("nba","NBA")
plot_data("politics","U.S. Politics")
plot_data("nfl","NFL")
plot_data("europe","Europe")
