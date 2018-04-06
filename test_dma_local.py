# -*- coding: utf-8 -*-
"""
Created on Wed Mar 14 20:40:23 2018

@author: helf
"""

import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
import api.quant_api as qapi
from api import logger


# 参数设置
trade_fee = 0.002
N_volt = 24
volt_mul = 2.0
N_short = 6
N_long_1 = 72
N_long_2 = 144

btc_data = pd.read_csv('btc_data_20171101_20180325.csv', index_col=0)
btc_data['close'] = btc_data['cp']
btc_data['strtime'] = btc_data['ts']
print(btc_data.head())

data = btc_data.iloc[0:60:60*N_long_2].copy()


# 变量初始化
data['ma'] = data['close']
data['ref'] = data['close']
data['signal'] = 0
data['account'] = 1
data['earning'] = 0
data['voltility'] = 0
data['pct_chg'] = 0


for each in btc_data.index[60*N_long_2::60]:

    # 获取当前时刻的bar
    
    bar_df = btc_data.loc[each]


    # 加入到历史数据中
    data = data.append(bar_df)

    now = data.index[-1]
    last = data.index[-2]
    # print(now)

    # 按收盘价交易，先计算账户每日涨跌
    data.loc[now, 'chg'] = data.loc[now, 'close'] - data.loc[last, 'close']
    data.loc[now, 'pct_chg'] = data.loc[now, 'close'] / data.loc[last, 'close'] - 1

    if data.loc[last, 'signal'] == 1:       # 做多区间
        data.loc[now, 'account'] = data.loc[last, 'account'] * (1 + data.loc[now, 'pct_chg'])
    elif data.loc[last, 'signal'] == -1:    # 做空区间
        data.loc[now, 'account'] = data.loc[last, 'account'] * (1 - data.loc[now, 'pct_chg'])
    else:
        data.loc[now, 'account'] = data.loc[last, 'account']

    # 收盘后，计算波动率，确定均线参数
    volt_last = data['chg'].iloc[-N_volt:].std()
    data.loc[now, 'voltility'] = volt_last

    if volt_last > data['voltility'].iloc[-N_long_2:].quantile(0.8):
        N_LONG = N_long_1
    else:
        N_LONG = N_long_2

    # 计算参考均线值
    data.loc[now, 'ma'] = (data.loc[last, 'ma'] * (N_short - 1) + data.loc[now, 'close'] * 2) / (N_short + 1)
    data.loc[now, 'ref'] = (data.loc[last, 'ref'] * (N_LONG - 1) + data.loc[now, 'close'] * 2) / (N_LONG + 1)

    # 向上突破，买入
    if (data.loc[last, 'ma'] < data.loc[last, 'ref']) and (data.loc[now, 'ma'] > data.loc[now, 'ref']):
        data.loc[now, 'signal'] = 1
        op_info = "%s 买入 BTC @ %f." %(now, data.loc[now, 'close'])
        logger.info(op_info)

        # 考虑手续费
        data.loc[now, 'account'] = data.loc[now, 'account'] * (1 - trade_fee)
        # 调整参考均线的值
        data.loc[now, 'ref'] = data.loc[now, 'ref'] - data.loc[now, 'voltility']*volt_mul

    # 向下突破，卖出
    elif (data.loc[last, 'ma'] > data.loc[last, 'ref']) and (data.loc[now, 'ma'] < data.loc[now, 'ref']):
        data.loc[now, 'signal'] = -1
        op_info = "%s 卖出 BTC @ %f." %(now, data.loc[now, 'close'])
        logger.info(op_info)


        # 考虑手续费
        data.loc[now, 'account'] = data.loc[now, 'account'] * (1 - trade_fee)
        # 调整参考均线的值
        data.loc[now, 'ref'] = data.loc[now, 'ref'] + data.loc[now, 'voltility']*volt_mul

    # 信号维持不变
    else:
        data.loc[now, 'signal'] = data.loc[last, 'signal']
        data.loc[now, 'account'] = data.loc[now, 'account']


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

result.to_csv('btc_dma_result.csv')
