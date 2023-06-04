import pandas as pd
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

	with open("data/basic_stats/"+kind+".csv","r") as inpuf:
		df = pd.read_csv(inpuf,sep = ";")
	df["tdate"] = df.apply(lambda x: datetime(int(x["date"].split("_")[0]),int(x["date"].split("_")[1]),int(x["date"].split("_")[2])), axis = 1)
	#activity ????????
	df = df.sort_values(by = ["tdate"])
	for col in ["posts","comments","leaves","fist_time_users","last_time_users","posts_per_author","comments_per_author"]:
		df[col] = df[col].rolling(7).mean()
	fig = plt.figure(figsize = (64,48))
	ax_posts = fig.add_subplot(4,1,1)
	ax_comments = fig.add_subplot(4,1,2)
	ax_comments_per_users = fig.add_subplot(4,1,3)
	ax_posts_per_users = fig.add_subplot(4,1,4)
	fontsize = 48
	#plot
	ax_posts_per_users.plot(df["tdate"],df["posts_per_author"],lw = 6, c = "blue")
	ax_posts_per_users.set_ylabel("Posts per Author",fontsize = fontsize)
	ax_posts_per_users.set_xlabel("Date",fontsize = fontsize)
	#
	ax_comments_per_users.plot(df["tdate"],df["comments_per_author"],lw = 6,c = "red")
	ax_comments_per_users.set_ylabel("Comments per Author",fontsize = fontsize)
	ax_comments_per_users.set_xlabel("Date",fontsize = fontsize)
	#
	ax_posts.plot(df["tdate"],df["posts"],lw = 6, c = "blue")
	ax_posts.set_ylabel("Posts",fontsize = fontsize)
	ax_posts.set_xlabel("Date",fontsize = fontsize)
	#
	ax_comments.plot(df["tdate"],df["comments"],lw = 6,c = "red")
	ax_comments.set_ylabel("Comments",fontsize = fontsize)
	ax_comments.set_xlabel("Date",fontsize = fontsize)
	#
	for ax in [ax_posts,ax_comments,ax_comments_per_users,ax_posts_per_users]:
		ax.tick_params(axis='both', which='major', labelsize = 32,size = 20)
		ax.tick_params(axis='both', which='minor', labelsize = 32,size = 20)
		ax_posts.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
		#add vertical line
		_, yup = ax.get_ylim()
		for event in dict_reddit_events[kind]:
			d = dict_events[event]
			ax.axvline(d, c = "orange", lw = 4)
			ax.text(d,yup,event,verticalalignment='center',fontsize = fontsize)
	fig.suptitle(title, fontsize = fontsize)
	#
	fig.tight_layout(rect = (0.0,0.0,1.0,0.98))
	fig.savefig("fig/bs_"+kind+".png")
plot_data("ukpolitics","UK Politics")
plot_data("nfl","NFL")

'''
plot_data("nba","NBA")
plot_data("politics","US Politics")
plot_data("soccer","Soccer")
plot_data("sports","Sports")
plot_data("cryptocurrency","Cryptocurrency")
plot_data("europe","Europe")
plot_data("science","Science")
plot_data("stocks","Stocks")
'''
