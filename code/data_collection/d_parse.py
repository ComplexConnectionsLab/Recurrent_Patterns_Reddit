import sys
import json
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('name', type=str)
name = parser.parse_args().name
what_parsing = "comments"
dict_sub_id = {
                "t5_2cneq":"politics",
                "t5_2qjfk":"stocks",
                "t5_2wlj3":"cryptocurrency",
                "t5_2qo4s":"nba",
                "t5_2qgzy":"sports",
                "t5_2qi58":"soccer",
                "t5_mouw":"science",
                "t5_2qh4j":"europe"
            }
dict_output_data = {v:[] for (k,v) in dict_sub_id.items()}
dict_idx = {v:1 for (k,v) in dict_sub_id.items()}
for line in sys.stdin:
    json_obj = json.loads(line)
    if json_obj["subreddit_id"] in dict_sub_id.keys():
        sub_name = dict_sub_id[json_obj["subreddit_id"]]
        dict_output_data[sub_name].append(json_obj)
        if len(dict_output_data[sub_name]) > 10**5:
            idx = dict_idx[sub_name]
            with open("data_raw/"+sub_name+"/"+what_parsing+"/"+name+"_"+str(idx)+".json","w") as outpuf:
                json.dump(dict_output_data[sub_name],outpuf)
            dict_idx[sub_name]+=1
            dict_output_data[sub_name] = []
for (sub_name,output_data) in dict_output_data.items():
    if len(output_data) > 0:
        idx = dict_idx[sub_name]
        with open("data_raw/"+sub_name+"/"+what_parsing+"/"+name+"_"+str(idx)+".json","w") as outpuf:
            json.dump(output_data,outpuf)
#zstd -cdq --long=31 dp/RC_2020-12.zst | python3 parse.py RC_2020_12
#zstd -cdq --long=31 dp/RC_2021-01.zst | python3 parse.py RC_2021_01
