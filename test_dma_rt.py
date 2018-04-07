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
from api import logger

exchange = 'huobipro'
symbol = 'btcusdt'
bar_type = '60min'

# 参数设置
trade_fee = 0.002
N_volt = 24
N_ma = 6
N_short = 24
N_long = 24*3

kline_data = qapi.get_bars(exchange=exchange, symbol_list=symbol, bar_type=bar_type, size=2*N_long)
kline =  qapi.to_dataframe(kline_data)
kline.index = kline['strtime']
kline = kline.sort_values(by='strtime')

# 变量初始化
kline['ma'] = kline['close'].copy()
kline['ref'] = kline['close'].copy()
kline['signal'] = 0
kline['account'] = 1
kline['earning'] = 0
kline['chg'] = kline['close'].diff(1)
kline['pct_chg'] = kline['close'].diff(1)/kline['close']
kline['voltility'] = kline['chg'].rolling(N_volt).std()
last_time = kline.index[-1]

logger.info('DMA 测试开始工作！')
while(1):

    last_bars = qapi.get_last_bars(exchange='huobipro', symbol_list='btcusdt', bar_type=bar_type)
    current = last_bars[0].strtime
    if current != last_time:      # 每隔1小时判断一次

        logger.info(current)
        last_time = current

        data = qapi.to_dataframe(last_bars)
        data.index = data['strtime']
        kline = kline.iloc[1:].append(data)

        now = kline.index[-1]
        last = kline.index[-2]

        # 按收盘价交易，先计算账户每日涨跌
        data.loc[now, 'chg'] = data['close'].iloc[-1] - data['close'].iloc[-2]
        data.loc[now, 'pct_chg'] = data['close'].iloc[-1] / data['close'].iloc[-2] - 1

        # 计算波动率，确定长均线参数
        data.loc[now, 'voltility'] = np.std(data['chg'].iloc[-N_volt:])

        if data['voltility'].iloc[-1] > data['voltility'].iloc[-N_long:].quantile(0.8):
            N_ref = N_short
        else:
            N_ref = N_long

        if data.loc[now, 'signal'] == 1:      # 买入状态，做多
            data.loc[now, 'account'] = data.loc[last, 'account']*(1 - data.loc[now, 'pct_chg'])

        elif data.long[now, 'signal'] == -1:    # 卖出状态，做空
            data.loc[now, 'account'] = data.loc[last, 'account'] * (1 + data.loc[now, 'pct_chg'])

        elif data.long[now, 'signal'] == 0:     # 空仓
            data.loc[now, 'account'] = data.loc[last, 'account']

        # 计算参考均线值
        data.loc[now, 'ma'] = (data.loc[last, 'ma'] * (N_ma - 1) + data.loc[now, 'close'] * 2) / (N_ma + 1)
        data.loc[now, 'ref'] = (data.loc[last, 'ref'] * (N_ref - 1) + data.loc[now, 'close'] * 2) / (N_ref + 1)

        # 向上突破，买入
        if (data.loc[last, 'ma'] < data.loc[last, 'ref']) \
                and (data.loc[now, 'ma'] > data.loc[now, 'ref']):
            data.loc[now, 'signal'] = 1
            # 考虑手续费
            data.loc[now, 'account'] = data.loc[last, 'account']  * (1 - trade_fee)
            # 调整参考均线的值
            data.loc[now, 'ref'] = data.loc[now, 'ref'] - 1.5 * data.loc[now, 'voltility']
            logger.info('%s 做多 btcusdt @ %f' % (now, data.loc[now, 'close']))
            logger.send_sms('%s 做多 btcusdt @ %f' % (now, data.loc[now, 'close']), '13811892804')

        # 向下突破，卖出
        elif (data.loc[last, 'ma'] > data.loc[last, 'ref']) \
                and (data.loc[now, 'ma'] < data.loc[now, 'ref']):
            data.loc[now, 'signal'] = -1
            # 考虑手续费
            data.loc[now, 'account'] = data.loc[now, 'account'] * (1 - trade_fee)
            # 调整参考均线的值
            data.loc[now, 'ref'] = data.loc[now, 'ref'] + 1.5 * data.loc[now, 'voltility']
            logger.info('%s 做空 btcusdt @ %f' % (now, data.loc[now, 'close']))
            logger.send_sms('%s 做空 btcusdt @ %f' % (now, data.loc[now, 'close']), '13811892804')

        # 信号维持不变
        else:
            data.loc[now, 'signal'] = data.loc[last, 'signal']

    # 休眠59分钟
    time.sleep(60*59)