# -*- coding: utf-8 -*-
"""
Created on Wed Mar 14 20:40:23 2018

@author: helf
"""

import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
from api.quant_api import TradeAccount, to_dataframe, to_dict
from api import logger

# 参数设置
trade_fee = 0.001

Period = 30
N = 24*2
K1 = 1
K2 = 1


test_api_key = "a4594cdd-75b0037b-003d37ea-528bd"
test_secret_key = "5f0ea6d5-a4ff1afc-9c04e15a-9e3ba"

class Context():

    def __init__(self):
        self.initial_cash = None
        self.data = None
        self.account = None
        self.benchmark = None


def init(context):

    context.account = TradeAccount(exchange='hbp', api_key=test_api_key, api_secret=test_secret_key)
    context.data = context.account.get_bars(symbol_list='btcusdt', bar_type='1min', size=100)
    print(context.data)

    btc_data = to_dataframe(context.data)
    btc_data['open'] = btc_data['op']
    btc_data['high'] = btc_data['hp']
    btc_data['low'] = btc_data['lp']
    btc_data['close'] = btc_data['cp']
    btc_data['strtime'] = btc_data['ts']
    print(btc_data.head())

    data = btc_data[['open', 'high', 'low', 'close']].iloc[0:Period * N:Period].copy()

    # 变量初始化
    data['upper'] = data['close']
    data['lower'] = data['close']
    data['mid'] = data['close']

    data['signal'] = 0
    data['account'] = 1
    data['earning'] = 0
    data['voltility'] = 0
    data['pct_chg'] = 0


def handle_data(context):



    for each in btc_data.index[Period * N::Period]:

        # 获取当前时刻的bar
        bar_df = btc_data[['open', 'high', 'low', 'close']].loc[each]

        # 加入到历史数据中
        data = data.append(bar_df)

        now = data.index[-1]
        last = data.index[-2]
        # print(now)

        # 按收盘价交易，先计算账户每日涨跌
        data.loc[now, 'chg'] = data.loc[now, 'close'] - data.loc[last, 'close']
        data.loc[now, 'pct_chg'] = data.loc[now, 'close'] / data.loc[last, 'close'] - 1

        if data.loc[last, 'signal'] == 1:  # 做多区间
            data.loc[now, 'account'] = data.loc[last, 'account'] * (1 + data.loc[now, 'pct_chg'])

            # 在做多区间，如果收盘价向下突破中线，平多仓
            if (data.loc[last, 'close'] > data.loc[last, 'mid']) \
            and (data.loc[now, 'close'] < data.loc[now, 'mid']):
                data.loc[now, 'signal'] = 0
                op_info = "%s 平多仓 BTC @ %f." % (now, data.loc[now, 'close'])
                logger.info(op_info)

            gain = data.loc[now, 'close']/last_long_price - 1
            if gain < -0.03:     # 此次亏损超过3%，止损
                data.loc[last, 'signal'] = 0
                op_info = "%s 止损平多仓 BTC @ %f." % (now, data.loc[now, 'close'])
                logger.info(op_info)

        elif data.loc[last, 'signal'] == -1:  # 做空区间
            data.loc[now, 'account'] = data.loc[last, 'account'] * (1 - data.loc[now, 'pct_chg'])

            # 在做空区间，如果收盘价向上突破中线，平空仓
            if (data.loc[last, 'close'] < data.loc[last, 'mid']) \
            and (data.loc[now, 'close'] > data.loc[now, 'mid']):
                data.loc[now, 'signal'] = 0
                op_info = "%s 平空仓 BTC @ %f." % (now, data.loc[now, 'close'])
                logger.info(op_info)

            gain =  last_long_price / data.loc[now, 'close']- 1
            if gain < -0.03:     # 此次亏损超过3%，止损
                data.loc[last, 'signal'] = 0
                op_info = "%s 止损平空仓 BTC @ %f." % (now, data.loc[now, 'close'])
                logger.info(op_info)

        else:
            data.loc[now, 'account'] = data.loc[last, 'account']

        # 计算唐奇安通道参数
        data.loc[now, 'upper'] = np.max(data['high'].iloc[-N:-1])
        data.loc[now, 'lower'] = np.min(data['low'].iloc[-N:-1])
        data.loc[now, 'mid'] = (data.loc[now, 'upper'] + data.loc[now, 'lower'] )/ 2

        # 收盘价向上突破HH，买入
        if (data.loc[last, 'close'] < data.loc[last, 'upper']) \
            and (data.loc[now, 'close'] > data.loc[now, 'upper']) \
            and data.loc[last, 'signal'] != 1:

            data.loc[now, 'signal'] = 1
            last_long_price = data.loc[now, 'close']
            op_info = "%s 做多 BTC @ %f." % (now, data.loc[now, 'close'])
            logger.info(op_info)

            # 考虑手续费
            data.loc[now, 'account'] = data.loc[now, 'account'] * (1 - trade_fee)

        # 收盘价向下突破LL，，卖出
        elif (data.loc[last, 'close'] > data.loc[last, 'lower']) \
            and (data.loc[now, 'close'] < data.loc[now, 'lower']) \
            and data.loc[last, 'signal'] != -1:

            data.loc[now, 'signal'] = -1
            last_short_price = data.loc[now, 'close']
            op_info = "%s 做空 BTC @ %f." % (now, data.loc[now, 'close'])
            logger.info(op_info)

            # 考虑手续费
            data.loc[now, 'account'] = data.loc[now, 'account'] * (1 - trade_fee)

        # 信号维持不变
        else:
            data.loc[now, 'signal'] = data.loc[last, 'signal']
            data.loc[now, 'account'] = data.loc[now, 'account']



if __name__ == "__main__":




