from pymongo import MongoClient
import time
import pandas as pd
import numpy as np

from api.fund_perform_eval import PerformEval
# from api.quant_api import get_bars_local
# from api.quant_api import Indicator
# from api.connection import perform2db
from api import logger



client = MongoClient('47.75.69.176', 28005)
coin_db = client['bc_bourse_huobipro']
coin_db.authenticate('helifeng', 'w7UzEd3g6#he6$ahYG')
collection = coin_db['b_bch_kline']

data = collection.find({'per': "3", "ts": {"$gt": "2017-05-01 19:50:00"}})

hist_data = {}
for each in data:
    hist_data[each['ts']] = each

hist_df = pd.DataFrame.from_dict(hist_data, orient='index')
print(hist_df.head())

hist_df.to_csv('bch_20171101_20180512.csv')
