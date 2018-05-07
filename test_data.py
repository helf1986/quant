from pymongo import MongoClient

import pandas as pd
import numpy as np

'''

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

hist_df.to_csv('bch_20171101_20180501.csv')
'''

from api.fund_perform_eval import PerformEval
from api.quant_api import get_bars_local
from api.quant_api import Indicator

data = pd.read_csv('btc_netvalue.csv', index_col=0, header=0)
total_asset = 30000
data['netvalue'] = 1+ data['total_return']/total_asset
data['daily_return'] = data['daily_return']/total_asset

import time

data.index = [time.strftime('%Y-%m-%d', time.strptime(each, '%Y/%m/%d')) for each in data.index]




benchmark = get_bars_local(exchange='hbp', symbol_list='btcusdt', bar_type='1day', begin_time=data['date'].iloc[0], end_time=data['date'].iloc[-1])

performs = []
for nn in range(len(data)):
    netvalue = data['netvalue'].iloc[0:nn+1]
    result = PerformEval(net_value=netvalue, benchmark_value=netvalue, riskfree_rate=0.0, return_type='d')
    each_perform = Indicator()
    each_perform.transact_time = netvalue.index[nn]
    each_perform.currency = 'usdt'
    each_perform.total_amt = data['total_return'].iloc[nn]
    each_perform.daily_return = netvalue.iloc[-1]/netvalue[-2]-1
    each_perform.annual_return = result['annual_return']
    each_perform.max_drawdown = result['max_drawdown']
    each_perform.sharp_ratio = result['sharpe']
    each_perform.total_return = result['total_return']
    each_perform.win_ratio = result['win']
    each_perform.nav = netvalue.iloc[-1]
    each_perform.risk_ratio = each_perform.annual_return/each_perform.max_drawdown

    performs = performs + [each_perform]

from api.connection import perform2db
for each_perform in performs:
    perform2db(each_perform)

