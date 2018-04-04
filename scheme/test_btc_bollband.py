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
import matplotlib.pyplot as plt

# data = pd.read_excel('btcusd_gdax.xlsx', 'Sheet2', index_col=0, header=0)

kline_data = pd.read_csv('E:/helf/quant/btc_quant/letsquant_btc/local/huobi_kline_1min_btc_usdt.csv', index_col=False,
                         header=0)
# data.index = (data['kline_id']+8*3600)/86400+70*365+19
kline_data.index = [time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tmp)) for tmp in kline_data['kline_id']]
kline_data['close'] = kline_data['close_price']
print(kline_data.head())

'''
plt.figure(figsize=(6,12))
axe1 = plt.subplot(2,1,1)
data['close'].plot(ax=axe1)
axe2 = plt.subplot(2,1,2)
data['volume'].plot.bar(ax=axe2)
# plt.bar(data['volume'].index, data['volume'].values)
plt.tight_layout()
plt.show()
'''

# 参数设置
trade_fee = 0.002
N_volt = 100
N_short = 20
N_long = 100

data = kline_data.iloc[0:]
# 变量初始化
data['upper'] = data['close']
data['middle'] = data['close']
data['lower'] = data['close']
data['signal'] = 0
data['account'] = 1
data['earning'] = 0
data['voltility'] = 0
data['pct_chg'] = 0

for nn in range(N_long + 1, len(data)):

    today = data.index[nn]
    last_day = data.index[nn - 1]
    print(today)

    # 收盘后，计算波动率，确定均线参数
    volt_last = data['chg'].iloc[nn - N_volt + 1:nn + 1].std()
    data.loc[today, 'voltility'] = volt_last

    if volt_last > data['voltility'].iloc[0:nn].quantile(0.8):
        N_MA = N_short
    else:
        N_MA = N_long

    # 计算Boll通道
    data.loc[today, 'mid'] = (data.loc[last_day, 'mid'] * (N_MA - 1) + data.loc[today, 'close'] * 2) / (N_MA + 1)
    data.loc[today, 'upper'] = data.loc[last_day, 'mid'] + 2* data.loc[last_day, 'chg']
    data.loc[today, 'lower'] = data.loc[last_day, 'mid'] - 2* data.loc[last_day, 'chg']
    
plt.figure(figsize=(12,6))
data[['close', 'mid', 'upper', 'lower']].plot()
plt.show()
