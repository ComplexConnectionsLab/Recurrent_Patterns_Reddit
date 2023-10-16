import sqlite3
import pandas as pd
import numpy as np
import json
import re
import string
from tqdm import tqdm
from datetime import datetime
#nlp
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import gensim
from nltk.tokenize import RegexpTokenizer
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
import nltk
from nltk import word_tokenize
from gensim.models import Word2Vec

def clean_text_and_get_list(temp_string,en_stop,p_stemmer,tokenizer):
	#clean text
	all_text = temp_string.strip()
	#remove punctuation
	all_text = re.sub('[%s]' % re.escape(string.punctuation)," ",all_text)
	#remove ’
	all_text = re.sub('’',' ',all_text)
	all_text = re.sub('“',' ',all_text)
	all_text = re.sub('“',' ',all_text)
	#lower text
	all_text = all_text.lower()
	#tokenize
	tokens = tokenizer.tokenize(all_text)
	#remove stopwords
	stopped_tokens = [i for i in tokens if not i in en_stop]
	# stem tokens
	stemmed_tokens = {i:p_stemmer.stem(i) for i in stopped_tokens}
	return stemmed_tokens,stopped_tokens

def create_data(database):
	sia = SentimentIntensityAnalyzer()
	#sqlite
	def dict_factory(cursor, row):
		d = {}
		for idx, col in enumerate(cursor.description):
			d[col[0]] = row[idx]
		return d
	conn = sqlite3.connect("./data/"+database+".db")
	conn.row_factory = dict_factory
	c = conn.cursor()
	#get users
	c.execute('SELECT author, week, ddd, count(*) as c FROM (SELECT author, author_id, week, year || "_" || week as ddd FROM submissions UNION ALL SELECT author, author_id, week, year || "_" || week as ddd FROM comments) GROUP BY author, ddd HAVING c > 5')
	tmp_week_users = {}
	wu_df = []
	for row in c:
		if row["author"].lower().endswith("bot"):
			continue
		if row["author"] == "AutoModerator":
			continue
		if row["author"] == "[deleted]":
			continue
		key = (row["ddd"].split("_")[0],row["ddd"].split("_")[1])
		if key not in tmp_week_users:
			tmp_week_users[key] = []
		tmp_week_users[key].append(row["author"])
		wu_df.append({"yw":key,"user":row["author"]})
	df = pd.DataFrame(wu_df)
	x = len(tmp_week_users.keys())
	gdf = df.groupby(by = ["user"]).count().reset_index()
	gdf["yw"] = gdf["yw"]/x
	gdf = gdf.sort_values(by = ["yw"],ascending = False)
	gdf = gdf[gdf["yw"]>0.5]
	users_to_mantain = set(gdf["user"].tolist())
	dict_week_users = {k:list(set(v).intersection(users_to_mantain)) for (k,v) in tmp_week_users.items()}
	select_posts = "SELECT * FROM submissions WHERE author == '{author}' AND week == '{week}' AND year == '{year}'"
	select_comms = "SELECT * FROM comments WHERE author == '{author}' AND week == '{week}' AND year == '{year}'"
	#nlp
	model = Word2Vec.load("data/w2v/all.model")
	tokenizer = RegexpTokenizer(r'\w+')
	en_stop = stopwords.words('english')
	p_stemmer = PorterStemmer()
	#get week
	output_data = {}
	for (week_year,users) in tqdm(dict_week_users.items(),total = len(dict_week_users.keys())):
		year = week_year[0]
		week = week_year[1]
		year_week = week_year[0]+"_"+week_year[1]
		output_data[year_week] = []
		#z score
		try:
			with open("data/ngrams/"+database+"_"+year_week+".csv","r") as inpuf:
				df = pd.read_csv(inpuf)
		except:
			continue
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
		patterns = [row["pattern"].split(",")[0].replace(",","").replace("(","").replace("'","").replace("'","").strip() for _,row in z_df.iterrows()]
		patterns.extend([row["pattern"].split(",")[1].replace(")","").replace("(","").replace("'","").replace("'","").strip() for _,row in z_df.iterrows()])
		patterns = list(set(patterns))
		#w2v users
		output_data[year_week] = {}
		for user in users:
			vector_user = []
			user_activation_time = []
			user_excitement = []
			#posts
			c.execute(select_posts.format(author = user,year = year,week = week))
			for row in c:
				if row["text"] == "[removed]":
					temp_string = ""
				else:
					temp_string = row["title"].lower() + row["text"].lower()
				try:
					stemmed_tokens,stopped_tokens = clean_text_and_get_list(temp_string,en_stop,p_stemmer,tokenizer)
				except:
					continue
				flag = False
				#check if
				for stopped_token in stopped_tokens:
					if stopped_token in patterns:
						flag = True
				tmp_vector = []
				if flag:
					for stopped_token in stopped_tokens:
						try:
							vector = model.wv[stemmed_tokens[stopped_token]]
							tmp_vector.append(vector)
						except:
							continue
				if len(tmp_vector) > 0:
					excitement = sia.polarity_scores(row["title"].lower() + row["text"].lower())["compound"]
					tmp_vector = np.array(tmp_vector)
					vector = np.mean(tmp_vector,axis = 0)
					vector_user.append(vector)
					user_activation_time.append(int(row["utc"]))
					user_excitement.append(excitement)
			#comments
			c.execute(select_comms.format(author = user,year = year,week = week))
			c2 = conn.cursor()
			user_delta_t = []
			for row in c:
				if row["text"] == "[removed]":
					temp_string = ""
				else:
					temp_string = row["text"].lower()
				try:
					stemmed_tokens,stopped_tokens = clean_text_and_get_list(temp_string,en_stop,p_stemmer,tokenizer)
				except:
					continue
				flag = False
				#check if
				for stopped_token in stopped_tokens:
					if stopped_token in patterns:
						flag = True
				tmp_vector = []
				if flag:
					for stopped_token in stopped_tokens:
						try:
							vector = model.wv[stemmed_tokens[stopped_token]]
							tmp_vector.append(vector)
						except:
							continue
				if len(tmp_vector) > 0:
					excitement = sia.polarity_scores(row["text"].lower())["compound"]
					tmp_vector = np.array(tmp_vector)
					vector = np.mean(tmp_vector,axis = 0)
					vector_user.append(vector)
					user_activation_time.append(int(row["utc"]))
					user_excitement.append(excitement)
					#get time
					if row["id_parent"][:2] == "t3":
						#post
						c2.execute("SELECT * FROM submissions WHERE id_submission =='{id_link}'".format(id_link = row["id_parent"]))
						for res in c2:
							dt = int(row["utc"]) - int(res["utc"])
							if dt > 86400:
								continue
							user_delta_t.append(dt)

					elif row["id_parent"][:2] == "t1":
						#comments
						c2.execute("SELECT * FROM comments WHERE id_comment == '{id_link}'".format(id_link = row["id_parent"]))
						for res in c2:
							dt = int(row["utc"]) - int(res["utc"])
							if dt > 86400:
								continue
							user_delta_t.append(dt)
			#gran final'
			if len(vector_user) == 0:
				continue
			vector_user = np.array(vector_user)
			vector = np.mean(vector_user,axis = 0)
			argument = np.linalg.norm(vector_user-vector,axis = 1)
			argument = np.power(argument,2)
			s = np.sqrt(np.mean(argument))
			output_data[year_week][user] = {"w2v":float(s),"dt":user_delta_t,"activation_time":user_activation_time,"excitement":user_excitement}
	conn.close()
	with open("data/users/users_gyration_w2v_"+database+".json","w") as outpuf:
		json.dump(output_data,outpuf)


create_data("europe")
