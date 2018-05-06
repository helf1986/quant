# -*- coding: utf-8 -*-
# Author: Lifeng He

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import datetime

from pymongo import MongoClient
import common.HuobiClient as hb
import common.BinanceClient as bnb
from api import logger


class ExSymbol(object):
    '''
    交易所数字货币符号
    '''
    def __init__(self):
        self.symbol = ''                              # 交易代码
        self.exchange = ''                            # 交易所代码
        self.sec_id = ''                              # 证券ID


class TradeAccount(object):
    '''
    交易账户对象
    '''

    exchange = ''       # hbp: 火币pro, bnb: Binance, okc: okcoin
    api_key = ''
    api_secret = ''
    client = None
    currency = ''       # 以哪种数币作为基准，比如USDT、BTC


    def __init__(self, exchange, api_key, api_secret, currency='USDT'):
        '''
        指定交易所账户
        :param exchange:
        :param api_key:
        :param api_secret:
        :param currency:
        '''
        self.exchange = exchange
        self.api_key = api_key
        self.api_secret = api_secret
        self.currency = currency.upper()

        if self.exchange == 'hbp':
            self.client = hb.HuobiClient(self.api_key, self.api_secret)
        elif self.exchange == 'bnb':
            self.client = bnb.BinanceClient(self.api_key, self.api_secret)


    def get_instruments(self, sec_type=None, is_active=1):
        '''

        :param exchange:
        :param sec_type:
        :param is_active:
        :return:
        '''

        instrus = []
        if self.exchange == 'hbp':
            res = self.client.get_symbols()
            if res['status'] == 'ok':
                data = res['data']
                for each in data:
                    instru = Instrument()
                    instru.exchange = self.exchange
                    instru.symbol = each['base-currency'] + each['quote-currency']
                    instru.base_currency = each['base-currency']
                    instru.quote_currency = each['quote-currency']
                    instru.amount_precision = each['amount-precision']
                    instru.price_precision = each['price-precision']
                    instru.symbol_partition = each['symbol-partition']

                    instrus = instrus + [instru]
            else:
                logger.warn('No instruments found')

        elif self.exchange == 'bnb':
            pass

        return instrus


    def get_bars(self, symbol_list='btcusdt', bar_type='1min', begin_time='', end_time='', size=0):
        '''
        提取指定时间段的历史Bar数据，支持单个代码提取或多个代码组合提取。
        :param symbol_list: 证券代码, 带交易所代码以确保唯一，如SHSE.600000，同时支持多只代码
        :param bar_type: bar周期，1min, 5min, 15min, 30min, 60min, 1day, 1mon, 1week, 1year }
        :param begin_time: 开始时间, 如2015-10-30 09:30:00
        :param end_time: 结束时间, 如2015-10-30 15:00:00
        :param size: 取数数量，[1,2000]
        :return:
        '''

        symbol_list = symbol_list.replace(' ', '').split(',')
        bars = []

        if self.exchange == 'hbp':
            for each_sec in symbol_list:
                each_sec = each_sec.lower()         # 注意火币只支持小写字母

                inner_size = size
                if size == 0:
                    inner_size = 2000
                res = self.client.get_kline(symbol=each_sec, period=bar_type, size=inner_size)
                if res['status'] == 'ok':
                    data = res['data']
                    for each_bar in data:
                        bar = Bar()
                        bar.exchange = self.exchange
                        bar.sec_id = each_sec
                        bar.volume = each_bar['vol']
                        bar.amount = each_bar['amount']
                        bar.open = each_bar['open']
                        bar.high = each_bar['high']
                        bar.low = each_bar['low']
                        bar.close = each_bar['close']
                        bar.bar_type = bar_type
                        bar.utc_time = each_bar['id']
                        bar.strtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(each_bar['id']))
                        if size == 0:
                            if bar.strtime >= begin_time and bar.strtime <= end_time:
                                bars = bars + [bar]
                        else:
                            bars = bars + [bar]
                else:
                    logger.warn(res['err-code'] + ":" + res['error-msg'])

        elif self.exchange == 'bnb':

            interval = '1d'
            if bar_type == '1min':
                interval = '1m'
            elif bar_type == '5min':
                interval = '5m'
            elif bar_type == '15min':
                interval = '15m'
            elif bar_type == '30min':
                interval = '30m'
            elif bar_type == '60min':
                interval = '1h'
            elif bar_type == '1day':
                interval = '1d'
            elif bar_type == '1week':
                interval = '1w'

            startTime = time.mktime(time.strptime(begin_time, '%Y-%m-%d %H:%M:%S'))
            endTime = time.mktime(time.strptime(end_time, '%Y-%m-%d %H:%M:%S'))

            for each_sec in symbol_list:
                each_sec = each_sec.upper()         # 币安支持大写字母
                res = self.client.get_klines(symbol=each_sec, interval=interval, startTime=startTime, endTime=endTime)
                for each_bar in res:
                    bar = Bar()
                    bar.exchange = self.exchange
                    bar.sec_id = each_sec

                    bar.utc_time = int(each_bar[0])
                    bar.strtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(bar.utc_time / 1000))
                    bar.open = each_bar[1]
                    bar.high = each_bar[2]
                    bar.low = each_bar[3]
                    bar.close = each_bar[4]
                    bar.volume = each_bar[5]
                    bar.amount = each_bar[7]
                    bar.bar_type = bar_type
                    bar.utc_endtime = each_bar[6]
                    bar.strendtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(bar.utc_endtime / 1000))

                    bars = bars + [bar]

        return bars


    def get_last_ticks(self, symbol_list='btcusdt'):

        symbol_list = symbol_list.replace(' ', '').split(',')
        ticks = []

        if self.exchange == 'hbp':
            for each_sec in symbol_list:
                each_sec = each_sec.lower()
                tick_res = self.client.get_ticker(symbol=each_sec)
                # depth_res = hb.get_depth(symbol=each, type='step5')
                if tick_res['status'] == 'ok':
                    data = tick_res['tick']
                    tick = Tick()
                    tick.exchange = self.exchange
                    tick.sec_id = each_sec
                    tick.utc_time = tick_res['ts']
                    tick.strtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tick_res['ts'] / 1000))
                    tick.open = data['open']
                    tick.high = data['high']
                    tick.low = data['low']
                    tick.last_price = data['close']
                    tick.last_volume = data['vol']
                    tick.last_amount = data['amount']
                    tick.last_count = data['count']
                    tick.asks = [tuple(data['ask'])]
                    tick.bids = [tuple(data['bid'])]

                    ticks = ticks + [tick]
                else:
                    logger.warn('No data fechted!')

        elif self.exchange == 'bnb':

            for each_sec in symbol_list:
                each_sec = each_sec.upper()
                res = self.client.get_ticker(symbol=each_sec)
                tick = Tick()
                tick.exchange = self.exchange
                tick.sec_id = res['symbol']
                tick.pre_close = res['prevClosePrice']
                tick.open = res['openPrice']
                tick.high = res['highPrice']
                tick.low = res['lowPrice']
                tick.last_price = res['lastPrice']
                tick.last_volume = res['volume']
                tick.last_amount = res['quoteVolume']
                tick.vwap = res['weightedAvgPrice']
                tick.utc_time = res['openTime']
                tick.strtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tick.utc_time / 1000))
                tick.utc_endtime = res['closeTime']
                tick.strendtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tick.utc_endtime / 1000))
                tick.last_count = res['count']
                tick.asks = [(res['askPrice'], res['askQty'])]
                tick.bids = [(res['bidPrice'], res['bidQty'])]
                ticks = ticks + [tick]

        return ticks


    def get_last_bars(self, symbol_list='btcusdt', bar_type='1day'):
        '''

        :param symbol_list:
        :param bar_type: {1min, 5min, 15min, 30min, 60min, 1day, 1mon, 1week, 1year }
        :return:
        '''
        symbol_list = symbol_list.replace(' ', '').split(',')
        bars = []
        if self.exchange == 'hbp':
            for each_sec in symbol_list:
                each_sec = each_sec.lower()
                bar_res = self.client.get_kline(symbol=each_sec, period=bar_type, size=1)
                if bar_res['status'] == 'ok':
                    data = bar_res['data'][0]
                    bar = Bar()
                    bar.exchange = self.exchange
                    bar.sec_id = each_sec
                    bar.bar_type = bar_type
                    bar.utc_time = data['id']
                    bar.strtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data['id']))
                    bar.open = data['open']
                    bar.high = data['high']
                    bar.low = data['low']
                    bar.close = data['close']
                    bar.volume = data['vol']
                    bar.amount = data['amount']
                    bar.count = data['count']
                    bar.utc_endtime = bar_res['ts']
                    bar.strendtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(bar_res['ts'] / 1000))

                    bars = bars + [bar]
                else:
                    logger.warn('No bar data fetched!')

        elif self.exchange == 'bnb':

            endTime = time.mktime(time.localtime())
            interval = '1d'
            startTime = endTime - 24*60*60
            if bar_type == '1min':
                interval = '1m'
                startTime = endTime - 60
            elif bar_type == '5min':
                interval = '5m'
                startTime = endTime - 5* 60
            elif bar_type == '15min':
                interval = '15m'
                startTime = endTime - 15 * 60
            elif bar_type == '30min':
                interval = '30m'
                startTime = endTime - 20* 60
            elif bar_type == '60min':
                interval = '1h'
                startTime = endTime - 60 * 60
            elif bar_type == '1day':
                interval = '1d'
                startTime = endTime - 24 * 60 * 60
            elif bar_type == '1week':
                interval = '1w'
                startTime = endTime - 7*24 * 60 * 60

            for each_sec in symbol_list:
                each_sec = each_sec.upper()  # 币安只支持大写字母
                res = self.client.get_klines(symbol=each_sec, interval=interval, startTime=int(startTime*1000), endTime=int(endTime*1000))
                for each_bar in res:
                    bar = Bar()
                    bar.exchange = self.exchange
                    bar.sec_id = each_sec
                    bar.utc_time = int(each_bar[0])
                    bar.strtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(bar.utc_time / 1000))
                    bar.open = each_bar[1]
                    bar.high = each_bar[2]
                    bar.low = each_bar[3]
                    bar.close = each_bar[4]
                    bar.volume = each_bar[5]
                    bar.amount = each_bar[7]
                    bar.bar_type = bar_type
                    bar.utc_endtime = each_bar[6]
                    bar.strendtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(bar.utc_endtime / 1000))

                    bars = bars + [bar]

        return bars


    def get_depth(self, symbol='btcusdt', type='step1'):
        '''
        获取盘口深度数据
        :param exchange:
        :param symbol:
        :param type:
        :return:
        '''
        if self.exchange == 'hbp':
            symbol = symbol.lower()
            depth_res = self.client.get_depth(symbol=symbol, type=type)

        elif self.exchange == 'binance':
            symbol = symbol.upper()
            depth_res = self.cilent.get_order_book(symbol=symbol)

        return depth_res


    def open_long(self, source='api', sec_id='btcusdt', price=0, volume=0):
        '''
        异步开多仓，以参数指定的symbol、价和量下单。如果价格为0，为市价单，否则为限价单。
        :param exchange: string	交易所代码，如火币网：huobipro，OKCoin: okcoin
        :param source: string   订单接口源，api：普通订单，margin：融资融券订单
        :param sec_id: string   证券代码
        :param price: float     委托价，如果price=0,为市价单，否则为限价单
        :param volume: float	委托量
        :return: 委托下单生成的Order对象
        '''

        myorder = Order()
        myorder.exchange = self.exchange
        myorder.sec_id = sec_id
        myorder.price = price  ## 委托价
        myorder.volume = volume  ## 委托量
        myorder.cl_ord_id = ''

        myorder.position_effect = 1  ## 开平标志，1：开仓，2：平仓
        myorder.side = 1  ## 买卖方向，1：多方向，2：空方向

        if self.exchange == 'hbp':  # 火币网接口

            sec_id = sec_id.lower()
            if price == 0.0:
                mtype = 'buy-market'
                last_tick = self.get_last_ticks(symbol_list=sec_id)
                last_price = last_tick[0].last_price
                amount = volume * last_price
            else:
                mtype = 'buy-limit'
                amount = volume

            myorder.order_type = mtype  ## 订单类型
            myorder.order_src = source  ## 订单来源

            # 买入指定数字货币
            myorder.sending_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            if source == 'api':
                hb_source = 'api'
                res = self.cilent.send_order(amount=amount, source=hb_source, symbol=sec_id, _type=mtype, price=price)
            elif source == 'margin':
                hb_source = 'margin-api'
                res = self.client.send_margin_order(amount=amount, source=hb_source, symbol=sec_id, _type=mtype, price=price)

            if res['status'] == 'ok':
                myorder.ex_ord_id = int(res['data'])

                time.sleep(2)  # 等待2 秒后查询订单
                # 查询订单信息
                order_info = self.client.order_info(myorder.ex_ord_id)
                myorder.account_id = order_info['data']['account-id']
                myorder.status = order_info['data']['state']
                myorder.sending_time = time.strftime("%Y-%m-%d %H:%M:%S",
                                                     time.localtime(order_info['data']['created-at'] / 1000))
                myorder.filled_volume = float(order_info['data']['field-amount'])  ## 已成交量
                myorder.filled_amount = float(order_info['data']['field-cash-amount'])  ## 已成交额
                if (myorder.filled_volume > 0):
                    myorder.filled_vwap = round(myorder.filled_amount / myorder.filled_volume, 4)  ## 已成交均价
                myorder.filled_fee = float(order_info['data']['field-fees']) * last_price  ## 手续费
                myorder.transact_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(
                    order_info['data']['finished-at'] / 1000))  ## 最新一次成交时间

                logger.info('%s 订单号 %s：%s 开多仓，成交量 = %f，成交均价 = %f usdt，总成交额 = %f usdt，手续费 = %f usdt。' % \
                            (myorder.exchange, myorder.ex_ord_id, myorder.sec_id, myorder.filled_volume,
                             myorder.filled_vwap, myorder.filled_amount, myorder.filled_fee))

            elif res['status'] == 'error':
                myorder.status = res['status']
                myorder.ord_rej_reason = res['err-code']  ## 订单拒绝原因
                myorder.ord_rej_reason_detail = res['err-msg']  ## 订单拒绝原因描述
                logger.warn('%s 订单号 %s：%s 开多仓 %f 失败，失败编码：%s，具体原因：%s。' % \
                            (myorder.exchange, myorder.ex_ord_id, myorder.sec_id, myorder.volume, myorder.ord_rej_reason,
                            myorder.ord_rej_reason_detail))

        elif self.exchange == 'bnb':

            sec_id = sec_id.upper()
            if price == 0:
                order_type = 'MARKET'
                myorder.order_type = 'market'
            else:
                order_type = 'LIMIT'
                myorder.order_type = 'limit'

            order = self.client.create_order(symbol=sec_id,
                                        side='BUY',
                                        type=order_type,
                                        quantity=volume,
                                        price=price)

            myorder.transact_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(order['transactTime'] / 1000))
            myorder.order_id = order['orderId']
            myorder.ex_ord_id = order['clientOrderId']
            myorder.filled_amount = order['executedQty']
            myorder.filled_vwap = order['price']
            myorder.status = order['status']

        return myorder


    def close_long(self, source='api', sec_id='btcusdt', price=0, volume=0):
        '''
         异步平多仓，
         :param exchange: string	交易所代码，如火币网：huobipro，OKCoin: okcoin
         :param source: string   订单接口源，api：普通订单，margin-api：融资融券订单
         :param sec_id: string   证券代码，如
         :param price: float     委托价，如果price=0,为市价单，否则为限价单
         :param volume: float	委托量
         :return: 委托下单生成的Order对象
         '''

        myorder = Order()
        myorder.exchange = self.exchange
        myorder.sec_id = sec_id
        myorder.price = price  ## 委托价
        myorder.volume = volume  ## 委托量
        myorder.cl_ord_id = ''

        myorder.position_effect = 2  ## 开平标志，1：开仓，2：平仓
        myorder.side = 1  ## 买卖方向，1：多方向，2：空方向
        myorder.order_type = 0  ## 订单类型
        myorder.order_src = 0  ## 订单来源

        if self.exchange == 'hbp':  # 火币网接口
            sec_id = sec_id.lower()
            if price == 0.0:
                mtype = 'sell-market'
            else:
                mtype = 'sell-limit'

            myorder.sending_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

            if source == 'api':
                hb_source = 'api'
                res = self.client.send_order(amount=volume, source=hb_source, symbol=sec_id, _type=mtype, price=price)
            elif source == 'margin':
                hb_source = 'margin-api'
                res = self.client.send_margin_order(amount=volume, source=hb_source, symbol=sec_id, _type=mtype, price=price)

            if res['status'] == 'ok':
                myorder.ex_ord_id = int(res['data'])

                time.sleep(2)  # 等待3 秒后查询订单
                # 查询订单信息
                order_info = self.client.order_info(myorder.ex_ord_id)
                myorder.status = order_info['data']['state']
                myorder.account_id = order_info['data']['account-id']
                myorder.sending_time = time.strftime("%Y-%m-%d %H:%M:%S",
                                                     time.localtime(order_info['data']['created-at'] / 1000))
                myorder.filled_volume = float(order_info['data']['field-amount'])  ## 已成交量
                myorder.filled_amount = float(order_info['data']['field-cash-amount'])  ## 已成交额
                if (myorder.filled_volume > 0):
                    myorder.filled_vwap = round(myorder.filled_amount / myorder.filled_volume, 4)  ## 已成交均价
                myorder.filled_fee = float(order_info['data']['field-fees'])  ## 已成交额
                myorder.transact_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(
                    order_info['data']['finished-at'] / 1000))  ## 最新一次成交时间
                logger.info('%s 订单号 %s：%s 平多仓，成交量 = %f，成交均价 = %f usdt，总成交额 = %f usdt，手续费 = %f usdt。' % \
                            (myorder.exchange, myorder.ex_ord_id, myorder.sec_id, myorder.filled_volume,
                             myorder.filled_vwap, myorder.filled_amount, myorder.filled_fee))

            elif res['status'] == 'error':
                myorder.status = res['status']
                myorder.ord_rej_reason = res['err-code']  ## 订单拒绝原因
                myorder.ord_rej_reason_detail = res['err-msg']  ## 订单拒绝原因描述
                logger.warn('%s 订单号 %s：%s 平多仓 %f 失败，失败编码：%s，具体原因：%s。' % \
                            (myorder.exchange, myorder.ex_ord_id, myorder.sec_id, myorder.volume, myorder.ord_rej_reason,
                            myorder.ord_rej_reason_detail))

        elif self.exchange == 'bnb':

            sec_id = sec_id.upper()
            if price == 0:
                order_type = 'MARKET'
                myorder.order_type = 'market'
            else:
                order_type = 'LIMIT'
                myorder.order_type = 'limit'

            if myorder.side == 1:
                side = 'SIDE_BUY'
            else:
                side = 'SIDE_SELL'

            order = self.client.create_order(symbol=sec_id, side=side, type=order_type, quantity=volume, price=price)

            myorder.transact_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(order['transactTime'] / 1000))
            myorder.order_id = order['orderId']
            myorder.ex_ord_id = order['clientOrderId']
            myorder.filled_amount = order['executedQty']
            myorder.filled_vwap = order['price']
            myorder.status = order['status']

        return myorder


    def cancel_order(self, sec_id='', order_id=''):
        '''
        取消订单
        :param sec_id: 交易代码
        :param order_id: 订单号
        :return:
        '''

        if self.exchange == 'huobipro':
            res = self.client.cancel_order(order_id=order_id)
            if res['status'] == 'ok':
                return res['data']
            else:
                logger.warn(res['err-code'] + ':' + res['err-msg'])
                return None

        elif self.exchange == 'binance':
            sec_id = sec_id.upper()
            res = self.client.cancel_order(symbol=sec_id, orderId=order_id)
            return res['orderId']


    def apply_margin(self, symbol='btcusdt', currency='btc', amount=0):
        '''
        # 申请借贷
        :param symbol: 数字货币代码
        :param currency: 现金种类
        :param amount: 借贷额度
                 借贷最小额度：
                    usdt : 100
                    btc : 0.001
        :return:
        '''

        if self.exchange == 'hbp':
            symbol = symbol.lower()
            if currency == 'usdt':
                amount = round(amount, 2)
            elif currency == 'btc':
                amount = round(amount, 3)

            res = self.client.get_margin(symbol=symbol, currency=currency, amount=amount)
            if res['status'] == 'ok':
                margin_order_id = res['data']
                logger.info('%s 借贷订单号 %s：借入 %f %s' % (self.exchange, margin_order_id, amount, currency))
                return margin_order_id
            elif res['status'] == 'error':
                logger.warn(res['err-code'] + ":" + res['err-msg'])
                return False

        elif self.exchange == 'bnb':
            pass


    def repay_margin(self, order_id=None, amount=0):
        """
        # 归还借贷
        :param order_id:
        :param amount:
        :return:
        """

        if self.exchange == 'hbp':
            res = self.client.repay_margin(order_id=order_id, amount=amount)
            if res['status'] == 'ok':
                logger.info('%s 借贷订单号 %s：归还 %f' % (self.exchange, order_id, amount))
                return True
            elif res['status'] == 'error':
                logger.warn(res['err-code'] + ":" + res['err-msg'])
                return False

        elif self.exchange == 'bnb':
            pass


    def get_order(self, sec_id='', cl_ord_id=''):
        '''
        获取历史订单信息
        :param cl_ord_id:
        :return:
        '''

        if self.exchange == 'hbp':

            res = self.client.order_info(cl_ord_id)
            if res['status'] == 'ok':
                data = res['data']
                order = Order()
                order.exchange = self.exchange
                order.account_id = data['account-id']
                order.cl_ord_id = cl_ord_id
                order.order_id = data['id']
                order.order_src = data['source']
                order.status = data['state']
                order.sec_id = data['symbol']
                order.order_type = data['type']
                order.side = data['type']
                order.position_effect = data['type']
                order.sending_time = data['created-at']
                order.transact_time = data['finished-at']
                order.volume = float(data['amount'])
                order.price = float(data['price'])
                order.filled_amount = float(data['field-cash-amount'])
                order.filled_fee = float(data['field-fees'])
                order.filled_volume = float(data['field-amount'])
                if (order.filled_volume > 0):
                    order.filled_vwap = round(order.filled_amount / order.filled_volume, 4)  ## 已成交均价

                return order
            else:
                logger.warn(res['err-code'] + ":" + res['err-msg'])
                return None

        elif self.exchange == 'bnb':
            sec_id = sec_id.upper()
            res = self.client.get_all_orders(symbol=sec_id, orderId=cl_ord_id)
            order_list = []
            for each in res:
                order = Order()
                order.exchange = self.exchange
                order.sec_id = each['symbol']
                order.order_id = each['orderId']
                order.cl_ord_id = each['clientOrderId']
                if each['type'] == 'LIMIT':
                    order.order_type = 'limit'
                elif each['type'] == 'MARKET':
                    order.order_type = 'market'

                if each['side'] == 'BUY':
                    order.side = 1
                elif each['side'] == 'SELL':
                    order.side = 0

                order.transact_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(each['time'] / 1000))
                order.volume = each['origQty']
                order.price = each['price']
                order.filled_amount = each['executedQty']
                order.status = each['status']

                order_list = order_list + [order]

            return order_list


    def get_orders_by_symbol(self, sec_id='', begin_time='', end_time='', states='filled', types=None):
        '''
        获取指定 symbol 的历史交易记录
        :param sec_id:
        :param states: 查询的订单状态组合，使用','分割。pre-submitted 准备提交, submitted 已提交, partial-filled 部分成交, partial-canceled 部分成交撤销, filled 完全成交, canceled 已撤销
        :param types:  查询的订单类型组合，使用','分割。buy-market：市价买, sell-market：市价卖, buy-limit：限价买, sell-limit：限价卖
        :param start_time:
        :param end_time:
        :return:
        '''

        order_list = []
        if self.exchange == 'huobipro':
            sec_id = sec_id.lower()
            if states == 'all':
                states = 'pre-submitted,submitted,partial-filled,partial-canceled,filled,canceled'
            if types == 'all':
                types = 'buy-maret,sell-market,buy-limit,sell-limit'

            start_date = time.strftime('%Y-%m-%d', time.strptime(begin_time, '%Y-%m-%d %H:%M:%S'))
            end_date = time.strftime('%Y-%m-%d', time.strptime(end_time, '%Y-%m-%d %H:%M:%S'))
            res = self.client.orders_list(symbol=sec_id, states=states, types=types, start_date=start_date, end_date=end_date)
            if res['status'] == 'ok':
                data = res['data']

                for each in data:
                    order = Order()
                    order.exchange = self.exchange
                    order.status = each['state']
                    order.order_src = each['source']
                    order.account_id = each['account-id']
                    order.order_id = each['id']
                    order.transact_time = each['finished-at']
                    order.sending_time = each['created-at']
                    order.order_type = each['type']
                    order.sec_id = each['symbol']
                    order.price = each['price']
                    order.volume = each['amount']
                    order.filled_volume = float(each['field-amount'])
                    order.filled_amount = float(each['field-cash-amount'])
                    order.filled_fee = float(each['field-fees'])
                    if order.filled_volume > 0:
                        order.filled_vwap = round(order.filled_amount / order.filled_volume, 4)  ## 已成交均价

                    order_list = order_list + [order]
            else:
                logger.warn(res['err-code'] + ':' + res['err-msg'])

        elif self.exchange == 'bnb':

            sec_id = sec_id.upper()
            if states == 'all':
                states = ['NEW', 'PARTIALLY_FILLED', 'FILLED', 'CANCELED', 'PENDING_CANCEL', 'REJECTED', 'EXPIRED']
            else:
                states = states.split(',')

            if types == 'all':
                types = ['LIMIT', 'MARKET', 'STOP_LOSS', 'STOP_LOSS_LIMIT', 'TAKE_PROFIT', 'TAKE_PROFIT_LIMIT', 'LIMIT_MAKER']
            else:
                types = types.split(',')

            res = self.client.get_open_orders(symbol=sec_id)
            for each in res:
                order = Order()
                order.exchange = self.exchange
                order.sec_id = each['symbol']
                order.order_id = each['orderId']
                order.cl_ord_id = each['clientOrderId']
                if each['type'] == 'LIMIT':
                    order.order_type = 'limit'
                elif each['type'] == 'MARKET':
                    order.order_type = 'market'

                if each['side'] == 'BUY':
                    order.side = 1
                elif each['side'] == 'SELL':
                    order.side = 0

                order.transact_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(each['time'] / 1000))
                order.volume = each['origQty']
                order.price = each['price']
                order.filled_amount = each['executedQty']
                order.status = each['status']

                if (order.transact_time >= begin_time) and (order.transact_time <= end_time) and (order.status in states):
                    order_list = order_list + [order]

        return order_list


    def get_margin_orders(self, symbol='btcusdt', currency='btc', start_date="", end_date="", start="",
                          direct="", size=0):
        """
        # 借贷订单
        :param symbol:
        :param currency:
        :param direct: prev 向前，next 向后
        :return:
        """
        if self.exchange == 'hbp':

            symbol = symbol.lower()
            currency = currency.lower()
            res = self.client.loan_orders(symbol=symbol, currency=currency, start_date=start_date, end_date=end_date,
                                 start=start, direct=direct, size=str(size))
            if res['status'] == 'ok':
                if len(res['data']) > 0:
                    orders = res['data']
                    data_df = pd.DataFrame.from_dict(dict(zip(range(len(orders)), orders))).T
                    data_df.index = data_df['id']
                    data_df['interest-amount'] = data_df['interest-amount'].astype('float')
                    data_df['interest-balance'] = data_df['interest-balance'].astype('float')
                    data_df['interest-rate'] = data_df['interest-rate'].astype('float')
                    data_df['loan-amount'] = data_df['loan-amount'].astype('float')
                    data_df['loan-balance'] = data_df['loan-balance'].astype('float')
                    data_df['strtime'] = [time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(each / 1000)) for each in
                                          data_df['accrued-at']]
                    data_df = data_df[data_df['currency'] == currency]
                    data_df.sort_values(by='accrued-at', inplace=True)

                    return data_df
                else:
                    print('No history orders found!')
                    return None

            elif res['status'] == 'error':
                print(res['err-code'] + ":" + res['err-msg'])
                return None
        elif self.exchange == 'bnb':
            pass


    def get_margin_balance(self, symbol=''):
        '''

        :param symbol:
        :return:
        '''

        # 借贷账户详情,支持查询单个币种
        if self.exchange == 'hbp':
            symbol = symbol.lower()
            res = self.cleient.margin_balance(symbol=symbol)
            if res['status'] == 'ok':
                balance = res['data']['list']
                data_df = pd.DataFrame.from_dict(dict(zip(range(len(balance)), balance))).T
                data_df.index = data_df['currency']
                data_new = pd.DataFrame([], index=np.unique(data_df['currency']),
                                        columns=['trade', 'frozen', 'loan', 'interest', 'transfer-out-available',
                                                 'loan-available'])
                data_new['trade'] = data_df[data_df['type'] == 'trade']['balance']
                data_new['frozen'] = data_df[data_df['type'] == 'frozen']['balance']
                data_new['loan'] = data_df[data_df['type'] == 'loan']['balance']
                data_new['interest'] = data_df[data_df['type'] == 'interest']['balance']
                data_new['transfer-out-available'] = data_df[data_df['type'] == 'transfer-out-available']['balance']
                data_new['loan-available'] = data_df[data_df['type'] == 'loan-available']['balance']
                data_new = data_new.astype('float')
                return data_new
            else:
                return None
        elif self.exchange == 'bnb':
            pass


    def get_margin_volume(self, margin_order_id='', symbol='', currency=''):
        '''
        查询指定订单里未偿还的金额
        :param margin_order_id:
        :param symbol:
        :param currency:
        :return:
        '''

        unpaid_volume = 0

        if self.exchange == 'hbp':

            symbol = symbol.lower()
            currency = currency.lower()
            start = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            margin_orders = self.get_margin_orders(symbol=symbol, currency=currency, start=start, direct="prev", size=100)
            if margin_order_id in margin_orders.index:
                myorder = margin_orders.loc[margin_order_id]
                unpaid_volume = myorder['loan-balance'] + myorder['interest-balance']
            else:
                logger.warn('Margin order ID %d is not found!' % margin_order_id)

        elif self.exchange == 'bnb':
            pass

        return unpaid_volume


    def get_accounts(self):
        '''
        获取账户基本信息
        :param exchange: 交易所名称
        :return:
        '''
        if self.exchange == 'hbp':
            res = self.client.get_accounts()
            if res['status'] == 'ok':
                data = res['data']
                accounts = {}
                for each in data:
                    accounts[each['type']] = each
                return accounts
            else:
                return None
        elif self.exchange == 'bnb':
            pass


    def get_position(self, sec_id='btcusdt', side=0):
        '''

        :param sec_id:
        :param side:
        :return:
        '''
        positions = self.get_positions()
        position = Position()
        if self.exchange == 'hbp':
            sec_id = sec_id.lower()


    def get_positions(self, source='spot'):
        '''
        获得所有账户持仓情况
        :param source: spot: 普通账户，marign：借贷账户
        :return:
        '''

        positions = []
        if self.exchange == 'hbp':
            accounts = self.get_accounts()

            if source == 'spot':
                # 获取普通账户资金情况
                account = accounts['spot']['id']
            elif source == 'margin':
                # 获取融资融券账户资金情况
                account = accounts['margin']['id']
            else:
                logger.error('No accounts found from %s!' % source)

            res = self.client.get_balance(acct_id=account)
            if res['status'] == 'ok':
                account_info = res['data']
                account_id = account_info['id']
                account_type = account_info['type']
                account_status = account_info['state']
                account_balance = account_info['list']

                balance_dict = {}
                for each in account_balance:
                    balance_dict[each['currency']] = {}
                for each in account_balance:
                    balance_dict[each['currency']][each['type']] = each['balance']

                for each in balance_dict.keys():
                    position = Position()
                    position.exchange = self.exchange
                    position.account_id = account_id
                    position.account_type = account_type
                    position.account_status = account_status

                    position.sec_id = each
                    position.available = float(balance_dict[each]['trade'])
                    position.order_frozen = float(balance_dict[each]['frozen'])
                    position.amount = position.available + position.order_frozen
                    if source == 'margin':
                        position.loan = float(balance_dict[each]['loan'])
                        position.interest = float(balance_dict[each]['interest'])

                    positions = positions + [position]
            else:
                logger.warn(res['err-code'] + ':' + res['err-msg'])

        elif self.exchange == 'bnb':
            
            if source == 'spot':
                res = self.client.get_account()
                balance = res['balance']
                for each in balance:
                    if each['free'] > 0 or each['locked'] > 0:
                        position = Position()
                        position.exchange = self.exchange
                        position.available = each['free']
                        position.order_frozen = each['locked']
                        position.volume = each['free'] + each['locked']
                        positions = positions + [position]

        return positions


    def get_cash(self, source):

        '''
        获取账户中的现金资产（根据currency确定），包括可交易的、冻结的、借贷的
        :param source: 普通账户(api) or 借贷账户（margin_api)
        :return: Position 对象
        '''

        cash_position = Position()
        if self.exchange == 'hbp':
            positions = self.get_positions(source=source)
            cash_position = [each for each in positions if each.sec_id == self.currency]
            if len(cash_position) > 0:
                cash_position = cash_position[0]
        elif self.exchange == 'bnb':
            positions = self.get_positions(source=source)
            cash_position = [each for each in positions if each.sec_id == self.currency]
            if len(cash_position) > 0:
                cash_position = cash_position[0]

        return cash_position


def to_dict(obj):
    '''
    把对象转换成字典
    :param obj:
    :return: keys 为对象的属性，values 为属性值
    '''

    if isinstance(obj, object):
        return obj.__dict__

    elif isinstance(obj, list):
        obj_list = []
        for each in obj:
            obj_list = obj_list + [each.__dict__]
        return obj_list


def to_dataframe(obj_list):
    '''
    把对象列表转换成DataFrame
    :param obj_list: 对象的列表
    :return: DataFrame 格式，index 为序号，columns 为对象的属性
    '''

    obj_dict = [each.__dict__ for each in obj_list]
    obj_df = pd.DataFrame(obj_dict)
    return obj_df


class Instrument(object):
    def __init__(self):
        self.exchange = ''
        self.symbol = ''                ## 交易代码
        self.sec_type = 0               ## 代码类型
        self.sec_name = ''              ## 代码名称
        self.base_currency = ''         ## 基础币种
        self.quote_currency = ''        ## string	计价币种
        self.price_precision = 0        ## string	价格精度位数（0为个位）
        self.amount_precision = 0       ## string	数量精度位数（0为个位）
        self.symbol_partition = ''      ## string	交易区	main主区，innovation创新区，bifurcation分叉区


class Order(object):
    '''
    订单对象
    '''

    def __init__(self):
        self.strategy_id = ''                 ## 策略ID
        self.account_id = ''                  ## 交易账号
        self.currency = ''                    ## 计价货币
        self.exchange = ''                    ## 交易所代码
        self.user_id = ''                     ## 交易所用户ID

        self.order_id = ''                    ## 策略订单ID
        self.ex_ord_id = ''                   ## 交易所订单ID
        self.sec_id = ''                      ## 证券ID
        self.position_effect = 0              ## 开平标志
        self.side = 0                         ## 买卖方向
        self.order_type = 0                   ## 订单类型
        self.order_src = 0                    ## 订单来源
        self.status = 0                       ## 订单状态
        self.ord_rej_reason = 0               ## 订单拒绝原因
        self.ord_rej_reason_detail = ''       ## 订单拒绝原因描述

        self.price = 0.0                      ## 委托价
        self.stop_price = 0.0                 ## 止损价
        self.volume = 0.0                     ## 委托量
        self.filled_volume = 0.0              ## 已成交量
        self.filled_vwap = 0.0                ## 已成交均价
        self.filled_amount = 0.0              ## 已成交额
        self.filled_fee = 0.0                 ## 已成交交易费

        self.sending_time = 0.0               ## 委托下单时间
        self.transact_time = 0.0              ## 最新一次成交时间

        self.margin_order_id = ''             ### 融资融券订单号
        self.margin_currency = ''             ### 融资融券品种
        self.margin_vol = 0                   ### 融资融券金额


class ExecRpt(object):
    '''
    订单执行结果
    '''
    def __init__(self):
        self.strategy_id = ''                 ## 策略ID

        self.cl_ord_id = ''                   ## 客户端订单ID
        self.order_id = ''                    ## 交易所订单ID
        self.exec_id = ''                     ## 订单执行回报ID

        self.exchange = ''                    ## 交易所代码
        self.sec_id = ''                      ## 证券ID

        self.position_effect = 0              ## 开平标志
        self.side = 0                         ## 买卖方向
        self.ord_rej_reason = 0               ## 订单拒绝原因
        self.ord_rej_reason_detail = ''       ## 订单拒绝原因描述
        self.exec_type = 0                    ## 订单执行回报类型

        self.price = 0.0                      ## 成交价
        self.volume = 0.0                     ## 成交量
        self.amount = 0.0                     ## 成交额

        self.transact_time = 0.0              ## 交易时间


class Cash(object):
    '''
    账户现金
    '''
    def __init__(self):
        self.strategy_id = ''           ## 策略ID
        self.account_id = ''            ## 账户id
        self.currency = 0               ## 币种

        self.nav = 0.0                  ## 资金余额
        self.fpnl = 0.0                 ## 浮动收益
        self.pnl = 0.0                  ## 净收益
        self.profit_ratio = 0.0         ## 收益率
        self.frozen = 0.0               ## 持仓冻结金额
        self.order_frozen = 0.0         ## 挂单冻结金额
        self.available = 0.0            ## 可用资金

        self.cum_inout = 0.0            ## 累计出入金
        self.cum_trade = 0.0            ## 累计交易额
        self.cum_pnl = 0.0              ## 累计收益
        self.cum_commission = 0.0       ## 累计手续费

        self.last_trade = 0.0           ## 最新一笔交易额
        self.last_pnl = 0.0             ## 最新一笔交易收益
        self.last_commission = 0.0      ## 最新一笔交易手续费
        self.last_inout = 0.0           ## 最新一次出入金
        self.change_reason = 0          ## 变动原因

        self.transact_time = 0.0        ## 交易时间


class Position(object):
    '''
    账户持仓
    '''
    def __init__(self):
        self.strategy_id = ''           ## 策略ID
        self.account_id = ''            ## 账户id
        self.currency = ''              ## 计价货币
        self.exchange = ''              ## 交易所代码
        self.sec_id = ''                ## 证券ID
        self.side = 0                   ## 买卖方向，side=1：持有该资产，side =-1：持有该资产的借贷
        self.volume = 0.0               ## 持仓量
        self.order_frozen = 0.0         ## 挂单冻结仓位
        self.available = 0.0            ## 可平仓位
        self.loanvol = 0.0
        self.interest = 0.0
        self.loan_order_id = ''         # 仅对借贷资产有效，用于偿还借贷资产
        self.update_time = ''           ## 持仓更新时间


class Indicator(object):
    '''
    账户业绩指标
    '''
    def __init__(self):
        self.strategy_id = ''                       ## 策略ID
        self.account_id = ''                        ## 账号ID
        self.currency = ''                          ## 账户计价货币

        self.init = 0.0                             ## 账户初始资金
        self.total_amt = 0.0                        ## 当前账户总金额

        self.nav = 0.0                              ## 净值(cum_inout + cum_pnl + fpnl - cum_commission)
        self.pnl = 0.0                              ## 净收益(nav-cum_inout)
        self.profit_ratio = 0.0                     ## 收益率(pnl/cum_inout)
        self.profit_ratio_bench = 0.0               ## 基准收益率
        self.sharp_ratio = 0.0                      ## 夏普比率
        self.risk_ratio = 0.0                       ## 风险比率，波动率
        self.trade_count = 0                        ## 交易次数
        self.win_count = 0                          ## 盈利次数
        self.lose_count = 0                         ## 亏损次数
        self.win_ratio = 0.0                        ## 胜率
        self.max_profit = 0.0                       ## 最大收益
        self.min_profit = 0.0                       ## 最小收益
        self.max_single_trade_profit = 0.0          ## 最大单次交易收益
        self.min_single_trade_profit = 0.0          ## 最小单次交易收益
        self.daily_max_single_trade_profit = 0.0    ## 今日最大单次交易收益
        self.daily_min_single_trade_profit = 0.0    ## 今日最小单次交易收益
        self.max_position_value = 0.0               ## 最大持仓市值或权益
        self.min_position_value = 0.0               ## 最小持仓市值或权益
        self.max_drawdown = 0.0                     ## 最大回撤
        self.daily_pnl = 0.0                        ## 今日收益
        self.daily_return = 0.0                     ## 今日收益率
        self.total_return = 0.0                     ## 累计收益率
        self.annual_return = 0.0                    ## 年化收益率

        self.cum_inout = 0.0                        ## 累计出入金
        self.cum_trade = 0.0                        ## 累计交易额
        self.cum_pnl = 0.0                          ## 累计平仓收益(没扣除手续费)
        self.cum_commission = 0.0                   ## 累计手续费

        self.transact_time = 0.0                    ## 指标计算时间


class Tick(object):
    '''
    Tick 数据
    '''
    def __init__(self):
        self.exchange = ''          ## 交易所代码
        self.sec_id = ''            ## 证券ID
        self.utc_time = 0.0         ## 行情时间戳
        self.strtime = ''           ## 可视化时间
        self.last_price = 0.0       ## 最新价
        self.open = 0.0             ## 开盘价
        self.high = 0.0             ## 最高价
        self.low = 0.0              ## 最低价
        self.utc_endtime = 0.0      ## 结束时间
        self.strendtime = ''        ## 结束时间

        self.cum_volume = 0.0       ## 成交总量/最新成交量,累计值
        self.cum_amount = 0.0       ## 成交总金额/最新成交额,累计值
        self.cum_position = 0.0     ## 合约持仓量(期),累计值
        self.last_volume = 0        ## 瞬时成交量(中金所提供)
        self.last_amount = 0.0      ## 瞬时成交额

        self.upper_limit = 0.0      ## 涨停价
        self.lower_limit = 0.0      ## 跌停价
        self.settle_price = 0.0     ## 今日结算价
        self.trade_type = 0         ## (保留)交易类型,对应多开,多平等类型 0:'上一个tick没有成交量', 1:'双开', 2: '双平', 3: '多开', 4:'空开', 5: '空平', 6:'多平', 7:'多换', 8:'空换'
        self.pre_close = 0.0        ## 昨收价
        self.price_chg = 0.0

        self.bids = []  ## [(price, volume), (price, volume), ...] ## 1-5档买价,量
        self.asks = []  ## [(price, volume), (price, volume), ...] ## 1-5档卖价,量


class Bar(object):
    '''
    各种周期的Bar数据
    '''
    def __init__(self):
        self.exchange = ''       ## 交易所代码
        self.sec_id = ''         ## 证券ID

        self.bar_type = 0        ## bar类型，以秒为单位，比如1分钟bar, bar_type=60
        self.strtime = ''        ## Bar开始时间
        self.utc_time = 0.0      ## Bar开始时间
        self.strendtime = ''     ## Bar结束时间
        self.utc_endtime = 0.0   ## Bar结束时间
        self.open = 0.0          ## 开盘价
        self.high = 0.0          ## 最高价
        self.low = 0.0           ## 最低价
        self.close = 0.0         ## 收盘价
        self.volume = 0.0        ## 成交量
        self.amount = 0.0        ## 成交额
        self.pre_close = 0.0          ## 前收盘价
        self.position = None         ## 持仓量
        self.adj_factor = 1.0         ## 复权因子
        self.flag = 0                ## 除权出息标记


class TradeDate(object):
    '''
    交易日期、时间
    '''
    def __init__(self):
        self.utc_time = 0.0                 ## UTC时间戳[带毫秒]
        self.strtime = ''                   ## 交易日


def get_bars_local(exchange='hbp', symbol_list='btcusdt', bar_type='1min', begin_time='', end_time='', size=0):
    '''
    从mongodb 取数
    :param exchange:
    :param symbol_list:
    :param bar_type:
    :param begin_time:
    :param end_time:
    :param size:
    :return:
    '''
    symbol_list = symbol_list.replace(' ', '').split(',')
    bars = []
    for each_sec in symbol_list:

        if begin_time == '':

            end_time_ts = int(time.time())
            end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time_ts))
            if bar_type == '1min':
                N_bar = 60
                per = 1
            elif bar_type == '5min':
                N_bar = 60*5
                per = 3
            elif bar_type == '15min':
                N_bar = 60*15
                per = 4
            elif bar_type == '30min':
                N_bar = 60*60
                per = 5
            elif bar_type == '60min':
                N_bar = 60*60
                per = 6
            elif bar_type == '1day':
                N_bar = 60*60*24
                per = 14
            begin_time_ts = int(end_time_ts - N_bar * size)
            begin_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(begin_time_ts))

        client = MongoClient('47.75.69.176', 28005)
        coin_db = client['bc_bourse_huobipro']
        coin_db.authenticate('helifeng', 'w7UzEd3g6#he6$ahYG')
        collection = coin_db['b_btc_kline']

        data = collection.find({'per': str(per), "t": {"$gte": begin_time_ts, "$lte":end_time_ts}})

        for each_bar in data:
            # print(each_bar)
            bar = Bar()
            bar.exchange = exchange
            bar.sec_id = each_sec
            bar.volume = each_bar['amt']
            bar.amount = each_bar['vol']
            bar.open = each_bar['op']
            bar.high = each_bar['hp']
            bar.low = each_bar['lp']
            bar.close = each_bar['cp']
            bar.bar_type = bar_type
            bar.utc_time = each_bar['t']
            bar.strtime = each_bar['ts']

            bars = bars + [bar]

    return bars
