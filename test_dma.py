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
import api.quant_api as qapi


# 参数设置
trade_fee = 0.002
N_volt = 30
volt_mul = 2.0
N_short = 12
N_long_1 = 48
N_long_2 = 72


symbol = 'btcusdt'
kline_data = qapi.get_bars(exchange='huobipro', symbol_list=symbol, bar_type='1min', size=2*N_long_2)
kline_list = [each_bar.__dict__ for each_bar in kline_data]
kline_df = pd.DataFrame(kline_list)
kline_df.index = kline_df['strtime']
kline_df = kline_df.sort_values(by='utc_time')
print(kline_df.head())
data = kline_df[['utc_time', 'close', 'volume']]

# 变量初始化
data['ref'] = data['close']
data['signal'] = 0
data['account'] = 1
data['earning'] = 0
data['voltility'] = 0
data['pct_chg'] = 0

while (1):

    time_struct = time.localtime()
    time_str = time.strftime('%Y-%m-%d %H:%M:%S', time_struct)

    if time_struct.tm_sec == 0:

        tick = qapi.get_last_bars(exchange='huobipro', symbol_list='btcusdt', bar_type='1min')
        tick_df = qapi.to_dataframe(tick)

        now = data.index[nn]
        last = data.index[nn - 1]
        print(now)

        # 按收盘价交易，先计算账户每日涨跌
        data.loc[now, 'chg'] = data.loc[now, 'close'] - data.loc[last, 'close']
        data.loc[now, 'pct_chg'] = data.loc[now, 'close'] / data.loc[last, 'close'] - 1
        if data.loc[last, 'signal'] == -1:  # 做空
            data.loc[now, 'account'] = data.loc[last, 'account'] * (1 - data.loc[now, 'pct_chg'])

        elif data.loc[last, 'signal'] == 1:  # 做多
            data.loc[now, 'account'] = data.loc[last, 'account'] * (1 + data.loc[now, 'pct_chg'])
        else:
            data.loc[now, 'account'] = data.loc[last, 'account']

        # 收盘后，计算波动率，确定均线参数
        volt_last = data['chg'].iloc[nn - N_volt + 1:nn + 1].std()
        data.loc[now, 'voltility'] = volt_last

        if volt_last > data['voltility'].iloc[0:nn].quantile(0.8):
            N_MA = N_short
        else:
            N_MA = N_long

        # 计算参考均线值
        data.loc[now, 'ref'] = (data.loc[last, 'ref'] * (N_MA - 1) + data.loc[now, 'close'] * 2) / (N_MA + 1)

        # 向上突破，买入
        if (data.loc[last, 'close'] < data.loc[last, 'ref']) and (
                data.loc[now, 'close'] > data.loc[now, 'ref']):
            data.loc[now, 'signal'] = 1
            # 考虑手续费
            data.loc[now, 'account'] = data.loc[now, 'account'] * (1 - trade_fee)

            # 调整参考均线的值
            data.loc[now, 'ref'] = data.loc[now, 'ref'] - data.loc[now, 'voltility']

        # 向下突破，卖出
        elif (data.loc[last, 'close'] > data.loc[last, 'ref']) and (
                data.loc[now, 'close'] < data.loc[now, 'ref']):
            data.loc[now, 'signal'] = -1
            # 考虑手续费
            data.loc[now, 'account'] = data.loc[now, 'account'] * (1 - trade_fee)

            # 调整参考均线的值
            data.loc[now, 'ref'] = data.loc[now, 'ref'] + data.loc[now, 'voltility']

        # 信号维持不变
        else:
            data.loc[now, 'signal'] = data.loc[last, 'signal']
            data.loc[now, 'account'] = data.loc[now, 'account']


