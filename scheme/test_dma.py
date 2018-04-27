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
N_volt = 30
volt_mul = 2.0
N_short = 6
N_long_1 = 48
N_long_2 = 72


symbol = 'btcusdt'
kline_data = qapi.get_bars(exchange='huobipro', symbol_list=symbol, bar_type='1min', size=N_long_2+1)
kline_df = qapi.to_dataframe(kline_data)
kline_df.index = kline_df['strtime']
kline_df = kline_df.sort_values(by='utc_time')
# print(kline_df.head())
data = kline_df[['utc_time', 'close', 'volume']].copy()

# 变量初始化
data['ma'] = data['close']
data['ref'] = data['close']
data['signal'] = 0
data['account'] = 1
data['earning'] = 0
data['voltility'] = 0
data['pct_chg'] = 0

time.sleep(60)
logger.info('Start:')
logger.send_sms('start btc operation!', '13811892804')

while (1):

    time_struct = time.localtime()
    time_str = time.strftime('%Y-%m-%d %H:%M:%S', time_struct)

    if time_struct.tm_sec == 0:

        # 获取当前时刻的bar
        bars = qapi.get_last_bars(exchange='huobipro', symbol_list='btcusdt', bar_type='1min')
        bar_df = qapi.to_dataframe(bars)
        bar_df.index = bar_df['strtime']

        # 加入到历史数据中
        data = data.iloc[1:].append(bar_df)

        now = data.index[-1]
        last = data.index[-2]
        print(now)

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
            logger.send_sms(op_info, '13811892804')

            # 考虑手续费
            data.loc[now, 'account'] = data.loc[now, 'account'] * (1 - trade_fee)
            # 调整参考均线的值
            data.loc[now, 'ref'] = data.loc[now, 'ref'] - data.loc[now, 'voltility']*volt_mul

        # 向下突破，卖出
        elif (data.loc[last, 'ma'] > data.loc[last, 'ref']) and (data.loc[now, 'ma'] < data.loc[now, 'ref']):
            data.loc[now, 'signal'] = -1
            op_info = "%s 卖出 BTC @ %f." %(now, data.loc[now, 'close'])
            logger.info(op_info)
            logger.send_sms(op_info, '13811892804')

            # 考虑手续费
            data.loc[now, 'account'] = data.loc[now, 'account'] * (1 - trade_fee)
            # 调整参考均线的值
            data.loc[now, 'ref'] = data.loc[now, 'ref'] + data.loc[now, 'voltility']*volt_mul

        # 信号维持不变
        else:
            data.loc[now, 'signal'] = data.loc[last, 'signal']
            data.loc[now, 'account'] = data.loc[now, 'account']

        time.sleep(55)

