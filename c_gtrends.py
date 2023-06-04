import matplotlib.pyplot as plt
from pytrends.request import TrendReq
for x in ["nba","nfl"]:
    pytrends = TrendReq(hl='en-US', tz=360)
    df = pytrends.get_historical_interest([x],year_start = 2020,month_start = 1,day_start = 1,year_end = 2021,month_end = 2,day_end = 1,cat = 0,frequency = "daily",sleep = 0)
    df["date"] = df.index
    df.to_csv("data/gtrends_"+x+".csv",sep = ",",index = False)
