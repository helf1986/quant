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
collection = coin_db['b_iota_kline']

# btc, bch, eth, xrp, ltc, eos, dash, iota, neo, omg, ada

end_time = "2017-05-12 00:00:00"
data = collection.find({'per': "1", "ts": {"$gt": end_time}})

hist_data = {}
for each in data:
    hist_data[each['ts']] = each

hist_df = pd.DataFrame.from_dict(hist_data, orient='index')
print(hist_df.tail())

hist_df.to_csv('iota_20171101_20180512.csv')


