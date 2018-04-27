# -*- coding: utf-8 -*-
"""
Created on Fri Mar 16 18:23:02 2018

@author: helf
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Mar 14 20:40:23 2018

@author: helf
"""

import pandas as pd
import numpy as np
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import api.quant_api as qapi


# kline_data = pd.read_excel('btcusd_gdax.xlsx', 'Sheet2', index_col=0, header=0)
# kline_data = pd.read_csv('btc_data_20171101_20180329.csv', index_col=0, header=0)

# data.index = (data['kline_id']+8*3600)/86400+70*365+19
# kline_data = kline_data.drop_duplicates(subset=['ts'])
# print(len(kline_data))

symbol = 'btcusdt'
kline_data = qapi.get_bars(exchange='huobipro', symbol_list=symbol, bar_type='60min', size=1000)
kline_list = [each_bar.__dict__ for each_bar in kline_data]
kline_df = pd.DataFrame(kline_list)
kline_df.index = kline_df['strtime']
kline_df = kline_df.sort_values(by='utc_time')
print(kline_df.head())

kline_df.to_csv('btc_his.csv')

'''
plt.figure(figsize=(6,12))
axe1 = plt.subplot(2,1,1)
kline_data['close'].plot(ax=axe1)
axe2 = plt.subplot(2,1,2)
kline_data['volume'].plot.bar(ax=axe2)
# plt.bar(data['volume'].index, kline_data['volume'].values)
plt.tight_layout()
plt.show()
'''

# 参数设置
trade_fee = 0.002
N_volt = 30
N_short = 6
N_long_1 = 48
N_long_2 = 72
volt_mul = 2

data = kline_df[['utc_time', 'close', 'volume']].iloc[0:]
# 变量初始化
data['ma'] = data['close']
data['ref'] = data['close']
data['signal'] = 0
data['account'] = 1
data['earning'] = 0
data['voltility'] = 0
data['pct_chg'] = 0


for nn in range(N_long_2+1, len(data)):
    
    today = data.index[nn]
    last_day = data.index[nn-1]
    print(today)
    
    # 按收盘价交易，先计算账户每日涨跌     
    data.loc[today, 'chg'] = data.loc[today, 'close'] - data.loc[last_day, 'close']
    data.loc[today, 'pct_chg'] = data.loc[today, 'close']/data.loc[last_day, 'close'] - 1
    if data.loc[last_day, 'signal'] == -1:     # 做空
        data.loc[today, 'account'] = data.loc[last_day, 'account']*(1-data.loc[today, 'pct_chg'])
    elif data.loc[last_day, 'signal'] == 1:    # 做多
        data.loc[today, 'account'] = data.loc[last_day, 'account']*(1+data.loc[today, 'pct_chg'])
    else:
        data.loc[today, 'account'] = data.loc[last_day, 'account']
    
    # 收盘后，计算波动率，确定均线参数
    volt_last = data['chg'].iloc[nn-N_volt+1:nn+1].std()
    data.loc[today, 'voltility'] = volt_last
    if volt_last > data['voltility'].iloc[0:nn].quantile(0.8):
        N_LONG = N_long_1
    else:
        N_LONG = N_long_2
    
    # 计算参考均线值
    data.loc[today, 'ma'] = (data.loc[last_day, 'ma']*(N_short-1) + data.loc[today, 'close']*2)/(N_short+1)
    data.loc[today, 'ref'] = (data.loc[last_day, 'ref']*(N_LONG-1) + data.loc[today, 'close']*2)/(N_LONG+1)
    
    # 向上突破，买入
    if (data.loc[last_day, 'ma'] < data.loc[last_day, 'ref']) and (data.loc[today, 'ma'] > data.loc[today, 'ref']):
        data.loc[today, 'signal'] = 1
        # 考虑手续费
        data.loc[today, 'account'] = data.loc[today, 'account']*(1-trade_fee)
        
        # 调整参考均线的值
        data.loc[today, 'ref'] = data.loc[today, 'ref'] - data.loc[today, 'voltility']*volt_mul
    
    # 向下突破，卖出
    elif (data.loc[last_day, 'ma'] > data.loc[last_day, 'ref']) and (data.loc[today, 'ma'] < data.loc[today, 'ref']):
        data.loc[today, 'signal'] = -1
        # 考虑手续费
        data.loc[today, 'account'] = data.loc[today, 'account']*(1-trade_fee)
        
        # 调整参考均线的值
        data.loc[today, 'ref'] = data.loc[today, 'ref'] + data.loc[today, 'voltility']*volt_mul
        
    # 信号维持不变
    else:
        data.loc[today, 'signal'] = data.loc[last_day, 'signal']
        data.loc[today, 'account'] = data.loc[today, 'account']


result = data.iloc[N_long_2:]
result['benchmark'] = result['close']/result['close'].iloc[0]*result['account'].iloc[0]
fig = plt.figure(figsize=(12,12))
ax1 = fig.add_subplot(211)
result[['close', 'ma', 'ref']].plot(ax=ax1)
ax1.set_ylabel('Close')

ax2 = ax1.twinx()  # this is the important function
ax2.plot(result.index, result['signal'], 'r')
ax2.set_ylabel('Signal')

ax3 = fig.add_subplot(212)
result[['account', 'benchmark']].plot(ax=ax3)
plt.savefig('test.png')

result.to_csv('btc_result.csv')

