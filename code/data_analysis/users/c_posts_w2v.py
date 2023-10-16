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

def create_data(database,output_data,select_posts,year_week,model,tokenizer,en_stop,p_stemmer):
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
    key = str(year_week[0])+"_"+str(year_week[1])
    output_data[key] = {}
    #comments
    select_comms = "SELECT * FROM comments WHERE id_submission = '{id_link}' ORDER BY cast(utc as INT) ASC"
    for _,post in df_posts.iterrows():
        c.execute(select_comms.format(id_link = post["id_submission"]))
        tmp_array = []
        temp_string = post["title"].lower() + post["text"].lower()
        stemmed_tokens,stopped_tokens = clean_text_and_get_list(temp_string,en_stop,p_stemmer,tokenizer)
        tmp_vector = []
        for stopped_token in stopped_tokens:
            try:
                vector = model.wv[stemmed_tokens[stopped_token]]
                tmp_vector.append(vector)
            except:
                continue
        if len(tmp_vector) > 0:
            tmp_vector = np.array(tmp_vector)
            vector = np.mean(tmp_vector,axis = 0)
            vector = vector.tolist()
            tmp_array.append(vector)
        for comm in c:
            if comm["text"] == "[removed]":
                continue
            if comm["author"].lower().endswith("bot"):
                continue
            if comm["author"] == "AutoModerator":
                continue
            dt = int(comm["utc"]) - int(post["utc"])
            if dt > 86400:
                continue
            temp_string = comm["text"].lower()
            stemmed_tokens,stopped_tokens = clean_text_and_get_list(temp_string,en_stop,p_stemmer,tokenizer)
            tmp_vector = []
            for stopped_token in stopped_tokens:
                try:
                    vector = model.wv[stemmed_tokens[stopped_token]]
                    tmp_vector.append(vector)
                except:
                    continue
            if len(tmp_vector) > 0:
                tmp_vector = np.array(tmp_vector)
                vector = np.mean(tmp_vector,axis = 0)
                vector = vector.tolist()
                tmp_array.append(vector)
        #
        vector_post = np.array([x for x in tmp_array])
        vector = np.mean(vector_post,axis = 0)
        argument = np.linalg.norm(vector_post-vector,axis = 1)
        argument = np.power(argument,2)
        s = np.sqrt(np.mean(argument))
        #
        v = np.diff(vector_post,axis = 0)
        a = np.linalg.norm(v,axis = 1)
        velocity = np.mean(a)
        output_data[key][post["id_submission"]] = [velocity,s]
    conn.close()


def save_data(database):
    #nlp
    model = Word2Vec.load("data/w2v/all.model")
    tokenizer = RegexpTokenizer(r'\w+')
    en_stop = stopwords.words('english')
    p_stemmer = PorterStemmer()
    #
    year_weeks = [(2020,i) for i in range(1,54)]
    for i in range(1,5):
        year_weeks.append((2021,i))
    select_posts = "SELECT * FROM submissions WHERE year == '{year}' and week == '{week}'"
    output_data = {}
    for year_week in tqdm(year_weeks):
        create_data(database,output_data,select_posts,year_week,model,tokenizer,en_stop,p_stemmer)
    with open("data/w2v_posts/w2v_velocity_gyration_"+database+".json","w") as outpuf:
        json.dump(output_data,outpuf)


save_data("politics")
save_data("nba")
save_data("nfl")
save_data("europe")
