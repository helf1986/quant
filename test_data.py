from pymongo import MongoClient

import pandas as pd


client = MongoClient('47.75.69.176', 28005)
coin_db = client['bc_bourse_huobipro']
coin_db.authenticate('helifeng', 'w7UzEd3g6#he6$ahYG')
collection = coin_db['b_btc_kline']

data = collection.find({'per': "1", "ts": {"$gt": "2018-04-29 19:50:00"}})

hist_data = {}
for each in data:
    hist_data[each['ts']] = each

hist_df = pd.DataFrame.from_dict(hist_data, orient='index')
print(hist_df.head())

hist_df.to_csv('btc_data_20180429.csv')