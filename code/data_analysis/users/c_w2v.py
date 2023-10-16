import sqlite3
import pandas as pd
import numpy as np
import json
import re
import string
from tqdm import tqdm
from datetime import datetime
#nlp
import gensim
from nltk.tokenize import RegexpTokenizer
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
import nltk
from nltk import word_tokenize
from gensim.models import Word2Vec
from gensim.models.callbacks import CallbackAny2Vec
#
import sys
sys.setrecursionlimit(1_500)
class callback(CallbackAny2Vec):
	def __init__(self):
		self.epoch = 0
		self.loss_to_be_subed = 0

	def on_epoch_end(self, model):
		loss = model.get_latest_training_loss()
		loss_now = loss - self.loss_to_be_subed
		self.loss_to_be_subed = loss
		print('Loss after epoch {}: {}'.format(self.epoch, loss_now))
		self.epoch += 1
#
def create_data(database):
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
	c.execute("SELECT * FROM submissions")
	posts = []
	for post in c:
		if post["author"].lower().endswith("bot"):
			continue
		if post["author"] == "AutoModerator":
			continue
		posts.append(post)
	#stemming
	tokenizer = RegexpTokenizer(r'\w+')
	en_stop = stopwords.words('english')
	p_stemmer = PorterStemmer()
	#comms
	select_comms = "SELECT * FROM comments WHERE id_submission = '{id_link}' ORDER BY cast(utc as INT) ASC"
	sentences = []
	for post in tqdm(posts):
		c.execute(select_comms.format(id_link = post["id_submission"]))
		if post["text"] == "[removed]":
			temp_string = ""
		else:
			temp_string = post["title"].lower() + post["text"].lower()
		for comm in c:
			if comm["text"] == "[removed]":
				continue
			if post["author"].lower().endswith("bot"):
				continue
			temp_string += comm["text"].lower()
		all_text = temp_string.strip()
		#remove punctuation
		all_text = re.sub('[%s]' % re.escape(string.punctuation)," ",all_text)
		#remove ’
		all_text = re.sub('’',' ',all_text)
		all_text = re.sub('“',' ',all_text)
		all_text = re.sub('“',' ',all_text)
		#lower text
		all_text = all_text.lower()
		try:
			#tokenize
			tokens = tokenizer.tokenize(all_text)
			#remove stopwords
			stopped_tokens = [i for i in tokens if not i in en_stop]
			# stem tokens
			stemmed_tokens = [p_stemmer.stem(i) for i in stopped_tokens]
			sentences.append(stemmed_tokens)
		except:
			print(len(all_text))
	conn.close()
	model = Word2Vec(sentences = sentences,vector_size = 100, window = 3,min_count = 4,epochs = 100, compute_loss = True,callbacks = [callback()])
	model.save("data/w2v/"+database+".model")
#create_data("wsb")
create_data("europe")
