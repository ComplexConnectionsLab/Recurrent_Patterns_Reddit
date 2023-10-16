import json
from datetime import datetime
import pytz

def save_data(database,event_chosen):
    #events
    if database == "europe":
        event_chosen_string = "e"+event_chosen.replace(" ", "_").lower()
    else:
        event_chosen_string = event_chosen.replace(" ", "_").lower()
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
        year = v.year
        week = v.isocalendar()[1]
        dict_events[k] = str(year)+"_"+str(week)
    ev = dict_events[event_chosen]
    with open("data/w2v_posts/w2v_velocity_gyration_"+database+".json","r") as outpuf:
        data = json.load(outpuf)
    output_data = data[ev]
    with open("data/w2v_posts/w2v_velocity_gyration_"+event_chosen_string+".json","w") as outpuf:
        json.dump(output_data,outpuf)


save_data("nba","NBA Trades")
save_data("politics","US 2020")
save_data("nfl","NFL Kickoff Game")
save_data("europe","Brexit")
