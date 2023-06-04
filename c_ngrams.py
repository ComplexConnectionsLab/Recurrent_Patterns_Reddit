import sqlite3
import pandas as pd
import pytz
import json
from datetime import datetime
from tqdm import tqdm
from itertools import combinations
from random import sample
import nltk
from nltk import word_tokenize
from nltk.util import ngrams
import re
import string
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
def create_data(database,select_posts,year_week):
	#sqlite
	def dict_factory(cursor, row):
		d = {}
		for idx, col in enumerate(cursor.description):
			d[col[0]] = row[idx]
		return d
	#post
	conn = sqlite3.connect("./data/"+database+".db")
	conn.row_factory = dict_factory
	c = conn.cursor()
	c.execute(select_posts.format(year = str(year_week[0]), week = str(year_week[1])))
	posts = []
	for post in c:
		if post["text"] == "[removed]":
			continue
		if post["author"].lower().endswith("bot"):
			continue
		if post["author"] == "AutoModerator":
			continue
		posts.append(post)
	#get only TOP 100 by num comments
	df_posts = pd.DataFrame(posts)
	df_posts["num_comments"] = pd.to_numeric(df_posts["num_comments"])
	df_posts = df_posts.sort_values(by = ["num_comments"])
	df_posts = df_posts.tail(100)
	select_comms = "SELECT * FROM comments WHERE id_submission = '{id_link}' ORDER BY cast(utc as INT) ASC"
	temp_patterns = {}
	dict_post_text = {}
	#stemming
	tokenizer = RegexpTokenizer(r'\w+')
	en_stop = stopwords.words('english')
	regex = re.compile('[%s]' % re.escape(string.punctuation))
	for _,post in df_posts.iterrows():
		c.execute(select_comms.format(id_link = post["id_submission"]))
		temp_string = post["title"].lower() + post["text"].lower()
		for comm in c:
			if comm["text"] == "[removed]":
				continue
			if post["author"].lower().endswith("bot"):
				continue
			if post["author"] == "AutoModerator":
				continue
			dt = int(comm["utc"]) - int(post["utc"])
			if dt > 86400:
				continue
			temp_string += comm["text"].lower()
		tmp_string = regex.sub("",temp_string)
		dict_post_text[post["id_submission"]] = tmp_string
		tokens = nltk.word_tokenize(tmp_string)
		#remove stopwords
		stopped_tokens = [i for i in tokens if not i in en_stop]
		bigrams = ngrams(stopped_tokens,2)
		for bigram in bigrams:
			if bigram not in temp_patterns:
				temp_patterns[bigram] = 1
			else:
				temp_patterns[bigram] += 1
	conn.close()
	#count
	final_output = [{"pattern":k,"how_many_times":v} for (k,v) in temp_patterns.items()]
	dataframe_final = pd.DataFrame(final_output)
	dataframe_final = dataframe_final[(dataframe_final["how_many_times"] > 25) & (dataframe_final["how_many_times"] < 100)]
	true_patterns = dataframe_final["pattern"].tolist()
	#shuffle
	for x in range(100):
		dataframe_final[str(x)] = 0
	for x in tqdm(range(100),total = 100):
		temp_patterns = {}
		for _,post in df_posts.iterrows():
			temp_string = dict_post_text[post["id_submission"]]
			temp_string = ' '.join(sample(temp_string.split(" "),len(temp_string.split(" "))))
			tokens = nltk.word_tokenize(temp_string)
			stopped_tokens = [i for i in tokens if not i in en_stop]
			bigrams = ngrams(stopped_tokens,2)
			for bigram in bigrams:
				if bigram not in temp_patterns:
					temp_patterns[bigram] = 1
				else:
					temp_patterns[bigram] += 1
		#count
		for true_pattern in true_patterns:
			if true_pattern in temp_patterns:
				value = temp_patterns[true_pattern]
				dataframe_final.loc[dataframe_final['pattern']==true_pattern, [str(x)]] = value
	return dataframe_final
def save_word(database):
	year_weeks = [(2020,i) for i in range(1,54)]
	for i in range(1,5):
		year_weeks.append((2021,i))
	select_posts = "SELECT * FROM submissions WHERE year == '{year}' and week == '{week}'"
	output_data = {}
	for year_week in tqdm(year_weeks):
		dataframe_final = create_data(database,select_posts,year_week)
		key = str(year_week[0])+"_"+str(year_week[1])
		dataframe_final.to_csv("data/ngrams/"+database+"_"+key+".csv",sep = ",",index = False)

save_word("ukpolitics")
