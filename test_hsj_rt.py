import numpy as np
import pandas as pd
import os
import time

import api.quant_api as qapi
from api import logger

c1 = 1.75  # std 系数
l1 = 5  # avg追溯时期
length = 400  # 基准期
unit = 1
most = 2
bar_type = '5min'
# --------------
MarketPosition = 0  #
ini_mkp = 0
lastbatimer = None

# phone_list =  "13811892804"
phone_list =  "13811892804, 18512101480, 13910993289, 15818535870, 13911217190"

if __name__ == '__main__':
    # -----------初始化----------------------------
    # ------------取数据-------
    bars = qapi.get_bars_local(exchange='huobipro', symbol_list='btcusdt', bar_type=bar_type, size=5000)
    data = qapi.to_dataframe(bars)[-5000:]
    # -------------------
    data['hp'] = data['close'].rolling(length).max()
    data['lp'] = data['close'].rolling(length).min()
    data['temp'] = data['close'].apply(np.log) - data['close'].shift().apply(np.log)
    data['tot'] = (data['temp'].apply(np.abs)).rolling(length).sum()
    data['net'] = data['hp'].apply(np.log) - data['lp'].apply(np.log)
    data['nt'] = data['net'] / data['tot']
    data['move'] = (data['close'] / data['close'].shift(length) - 1) * 100
    data['avg'] = data['nt'].rolling(length * l1).mean()
    data['std'] = data['nt'].rolling(length * l1).std()
    # -------------------
    for i in range(len(data)):
        close = data.iloc[i]['close']
        hp = data.iloc[i]['hp']
        lp = data.iloc[i]['lp']
        nt = data.iloc[i]['nt']
        move = data.iloc[i]['move']
        avg = data.iloc[i]['avg']
        std = data.iloc[i]['std']
        incon1 = ((close - lp) / (hp - lp) >= 0.8) and (nt >= avg + c1 * std) and (ini_mkp != 1)
        incon2 = ((close - lp) / (hp - lp) <= 0.2) and (nt >= avg + c1 * std) and (ini_mkp != -1)
        outcon = nt <= avg and ini_mkp != 0
        if incon1:
            ini_mkp = 1
            print(data.iloc[i]['strtime'], "Buy 1")
        if incon2:
            ini_mkp = -1
            print(data.iloc[i]['strtime'], "Sellshort 1")
        if outcon:
            ini_mkp = 0
            print(data.iloc[i]['strtime'], "Buytocover||Sell 1")
    # ---------------------------------------
    close_ = list(data['close'][-length * l1:].values)
    hp_ = list(data['hp'][-2000:].values)
    lp_ = list(data['lp'][-2000:].values)
    tot_ = list(data['tot'][-2000:].values)
    net_ = list(data['net'][-2000:].values)
    nt_ = list(data['nt'][-2000:].values)

    # ===================
    MarketPosition = ini_mkp
    lastbartime = data.iloc[-1]['strtime']
    limit = 0

    '''
    msg = "Q-BTC 数字货币量化交易系统开始工作..."
    logger.info(msg)
    logger.send_sms(msg, phone_list)
    '''

    # -----------初始化完成----------------------------
    # --------------------------------------循环计算
    while (1):
        try:
            bar = qapi.get_bars(exchange='huobipro', symbol_list='btcusdt', bar_type=bar_type, size=1)
            bar = bar[0]

            if bar.strtime == lastbartime:
                continue
            else:
                lastbartime = bar.strtime
                close_.append(bar.close)
                close_.pop(0)
                close = close_[-1]
                move = (close_[-1] / close_[-length] - 1) * 100
                hp = np.max(close_[-length:])
                lp = np.min(close_[-length:])
                hp_.append(hp)
                hp_.pop(0)
                lp_.append(lp)
                lp_.pop(0)
                temp = [np.log(x) for x in close_[-length:]]
                tot_.append(np.sum(np.abs(np.diff(temp))))
                tot_.pop(0)
                net_.append(np.log(hp_[-1]) - np.log(lp_[-1]))
                net_.pop(0)
                nt = net_[-1] / tot_[-1]
                nt_.append(nt)
                nt_.pop(0)
                avg = np.mean(nt_[-length * l1])
                std = np.std(nt_[-length * l1])

                incon1 = ((close - lp) / (hp - lp) >= 0.8) and (nt >= avg + c1 * std) and (
                MarketPosition != 1) and limit <= most
                incon2 = ((close - lp) / (hp - lp) <= 0.2) and (nt >= avg + c1 * std) and (
                MarketPosition != -1) and limit <= most
                outcon = (nt < avg) and MarketPosition != 0
                outcon1 = (nt >= avg + c1 * std) and (limit >= most + 1) and MarketPosition != 0

                if (incon1):
                    # qapi.open_long(exchange='huobipro', source='margin-api', sec_id='btcusdt', price=0, volume=unit)
                    msg = "%s 开多仓 btcusdt @ %f" % (bar.strtime, bar.close)
                    logger.info(msg)
                    logger.send_sms(msg, phone_list)
                    limit = limit + 1
                    MarketPosition = 1

                if (incon2):
                    # qapi.marginsec_open(exchange='huobipro', sec_id='btcusdt', price=0, volume=unit)
                    msg = "%s 开空仓 btcusdt @ %f" % (bar.strtime, bar.close)
                    logger.info(msg)
                    logger.send_sms(msg, phone_list)
                    limit = limit + 1
                    MarketPosition = -1

                if (outcon):
                    if MarketPosition == 1:
                        # qapi.close_long(exchange='huobipro', source='margin-api', sec_id='btcusdt', price=0, volume=unit)
                        msg = "%s 平多仓 btcusdt @ %f" % (bar.strtime, bar.close)
                        logger.info(msg)
                        logger.send_sms(msg, phone_list)
                        limit = 0
                        MarketPosition = 0
                    if MarketPosition == -1:
                        # qapi.marginsec_close(exchange='huobipro', source='margin-api', sec_id='btcusdt', price=0, volume=unit)
                        msg = "%s 平空仓 btcusdt @ %f" % (bar.strtime, bar.close)
                        logger.info(msg)
                        logger.send_sms(msg, phone_list)
                        limit = 0
                        MarketPosition = 0
                if (outcon1):
                    if MarketPosition == 1:
                        # qapi.close_long(exchange='huobipro', source='margin-api', sec_id='btcusdt', price=0, volume=unit)
                        msg = "%s 平多仓 btcusdt @ %f" % (bar.strtime, bar.close)
                        logger.info(msg)
                        logger.send_sms(msg, phone_list)
                        MarketPosition = 0
                    if MarketPosition == -1:
                        # qapi.marginsec_close(exchange='huobipro', source='margin-api', sec_id='btcusdt', price=0, volume=unit)
                        msg = "%s 平空仓 btcusdt @ %f" % (bar.strtime, bar.close)
                        logger.info(msg)
                        logger.send_sms(msg, phone_list)
                        MarketPosition = 0

        except Exception as e:
            # 如果连接失败，则休眠10 秒，重新连接
            time.sleep(10)