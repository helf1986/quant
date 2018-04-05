# -*- coding: utf-8 -*-
# Author: Lifeng He

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import datetime

from pymongo import MongoClient
import common.HuobiServices as hb
from api import logger


class BrokerAccount(object):
    '''
    柜台账户
    '''
    def __init__(self):
        self.account_id = ''                         # 柜台账号ID
        self.username = ''                           # 柜台账号
        self.permissible = 0                         # 允许交易
        self.status = 0                              # 账号当前状态


class ExSymbol(object):
    '''
    交易所数字货币符号
    '''
    def __init__(self):
        self.symbol = ''                              # 交易代码
        self.exchange = ''                            # 交易所代码
        self.sec_id = ''                              # 证券ID



class StrategyBase(object):
    '''
    策略对象
    '''

    def __init__(self,
                 username='',
                 password='',
                 strategy_id='',
                 subscribe_symbols='',
                 mode=2,
                 td_addr='',
                 config_file=None,
                 config_file_encoding='utf-8'):
        self.username = username,
        self.password = password,
        self.strategy_id = strategy_id,
        self.subscribe_symbols = subscribe_symbols,
        self.mode = mode
        self.td_addr = td_addr
        self.config_file = config_file
        self.config_file_encoding = config_file_encoding

    def backtest_config(self,
                        start_time,
                        end_time,
                        initial_cash=1000000,
                        transaction_ratio=1,
                        commission_ratio=0,
                        slippage_ratio=0,
                        price_type=1,
                        bench_symbol='SHSE.000300',
                        check_cache=1):
        pass

    def run(self):
        pass


    def stop(self):
        pass


    def get_ticks(self, exchange='huobipro', symbol_list='btcusdt', begin_time='', end_time=''):
        return get_ticks(exchange=exchange, symbol_list=symbol_list, begin_time=begin_time, end_time=end_time)


    def get_bars(self, exchange='huobipro', symbol_list='btcusdt', bar_type='1min', begin_time='', end_time=''):
        return get_bars(exchange=exchange, symbol_list=symbol_list, bar_type=bar_type, begin_time=begin_time, end_time=end_time)


    def get_last_ticks(self, exchange='huobipro', symbol_list='btcusdt'):

        return get_last_ticks(exchange=exchange, symbol_list=symbol_list)


    def get_last_bars(self, exchange='huobipro', symbol_list='btcusdt', bar_type='1min'):

        return get_last_bars(exchange=exchange, symbol_list=symbol_list, bar_type=bar_type)



    def get_instruments(self, exchange='huobipro'):

        return get_instruments(exchange=exchange)


    def open_long(self, exchange='huobipro', sec_id='btcusdt', price=0, volume=0):

        return open_long(exchange=exchange, sec_id=sec_id, price=price, volume=0)


    def close_short(self, exchange='huobipro', sec_id='btcusdt', price=0, volume=0):

        return close_short(exchange=exchange, sec_id=sec_id, price=price, volume=0)


    def open_short(self, exchange='huobipro', sec_id='btcusdt', price=0, volume=0):

        return open_short(exchange=exchange, sec_id=sec_id, price=price, volume=volume)


    def close_short(self, exchange='huobipro', sec_id='btcusdt', price=0, volume=0):

        return close_short(exchange=exchange, sec_id=sec_id, price=price, volume=volume)


    def cancel_order(self, exchange='huobipro', cl_ord_id=''):

        return cancel_order(exchange=exchange, cl_ord_id=cl_ord_id)


    def get_order(self, exchange='huobipro', cl_ord_id=''):

        return get_order(exchange=exchange, cl_ord_id=cl_ord_id)


    def get_orders_by_symbol(self, exchange='huobipro', start_time='', end_time=''):

        return get_orders_by_symbol(exchange=exchange, start_time=start_time, end_time=end_time)


    def get_cash(self):

        return get_cash()


    def get_position(self, exchange='huobipro', sec_id='btcusdt', side=0):

        return get_position(exchange=exchange, sec_id=sec_id, side=side)


    def get_positions(self, exchange='huobipro'):

        return get_positions(exchange='huobipro')


def to_dict(obj):
    '''
    把对象转换成字典
    :param obj:
    :return: keys 为对象的属性，values 为属性值
    '''
    return obj.__dict__


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

        self.cl_ord_id = ''                   ## 客户端订单ID
        self.order_id = ''                    ## 柜台订单ID
        self.ex_ord_id = ''                   ## 交易所订单ID

        self.exchange = ''                    ## 交易所代码
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
        self.margin_amount = 0                 ### 融资融券金额


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
        self.exchange = ''              ## 交易所代码
        self.sec_id = ''                ## 证券ID

        self.side = 0                   ## 买卖方向，side=1：持有该资产，side =-1：持有该资产的借贷
        self.volume = 0.0               ## 持仓量
        self.order_frozen = 0.0         ## 挂单冻结仓位
        self.available = 0.0            ## 可平仓位
        self.loan = 0.0
        self.interest = 0.0
        self.loan_order_id = ''         # 仅对借贷资产有效，用于偿还借贷资产


class Indicator(object):
    '''
    账户业绩指标
    '''
    def __init__(self):
        self.strategy_id = ''                       ## 策略ID
        self.account_id = ''                        ## 账号ID

        self.nav = 0.0                              ## 净值(cum_inout + cum_pnl + fpnl - cum_commission)
        self.pnl = 0.0                              ## 净收益(nav-cum_inout)
        self.profit_ratio = 0.0                     ## 收益率(pnl/cum_inout)
        self.profit_ratio_bench = 0.0               ## 基准收益率
        self.sharp_ratio = 0.0                      ## 夏普比率
        self.risk_ratio = 0.0                       ## 风险比率
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


def get_instruments(exchange, sec_type=None, is_active=1):
    '''

    :param exchange:
    :param sec_type:
    :param is_active:
    :return:
    '''

    instrus = []
    if exchange == 'huobipro':
        res = hb.get_symbols()
        if res['status'] == 'ok':
            data = res['data']
            for each in data:
                instru = Instrument()
                instru.exchange = exchange
                instru.symbol = each['base-currency'] + each['quote-currency']
                instru.base_currency = each['base-currency']
                instru.quote_currency = each['quote-currency']
                instru.amount_precision = each['amount-precision']
                instru.price_precision = each['price-precision']
                instru.symbol_partition = each['symbol-partition']

                instrus = instrus + [instru]
        else:
            logger.warn('No instruments found')

    return instrus


def get_positions(exchange):
    '''

    :param exchange:
    :return:
    '''

    positions = []
    if exchange == 'huobipro':

        account_id = get_accounts(exchange=exchange)

        # 先获取融资账户资金
        margin_account = account_id['margin']['id']
        res = hb.get_balance(acct_id=margin_account)
        if res['status'] == 'ok':
            balance = res['data']
            for each in balance:
                if each['trade'] > 0 or each['frozen'] > 0:
                    position = Position()
                    position.exchange = exchange
                    position.account_id = account_id
                    position.available = each['trade']
                    position.order_frozen = each['frozen']
                    position.volume = each['trade'] + each['frozen']
                    positions = positions + [position]
        else:
            logger.warn(res['err-code'] + ':' + res['err-msg'])

    return positions


def get_accounts(exchange='huobipro'):
    '''
    获取账户基本信息
    :param exchange: 交易所名称
    :return:
    '''
    if exchange == 'huobipro':
        res = hb.get_accounts()
        if res['status'] == 'ok':
            data = res['data']
            accounts = {}
            for each in data:
                accounts[each['type']] = each
            return accounts
        else:
            return None


def get_margin(exchange='huobipro', symbol=None, currency=None, amount=0):
    """
    # 申请借贷
    :param symbol: 数字货币代码
    :param currency: 现金种类
    :param amount: 借贷额度
    :return:
    """
    if exchange == 'huobipro':
        res =  hb.get_margin(symbol=symbol, currency=currency, amount=amount)
        if res['status'] == 'ok':
            margin_order_id = res['data']
            logger.info('%s 借贷订单号 %s：借入 %f %s' % (exchange, margin_order_id, amount, currency))
            return margin_order_id
        elif res['status'] == 'error':
            print(res['err-code'] + ":" + res['err-msg'])
            return False


def repay_margin(exchange='huobipro', order_id=None, amount=0):
    """
    # 归还借贷
    :param order_id:
    :param amount:
    :return:
    """

    if exchange == 'huobipro':
        res = hb.repay_margin(order_id=order_id, amount=amount)
        if res['status'] == 'ok':
            logger.info('%s 借贷订单号 %s：归还 %f' % (exchange, order_id, amount))
            return True
        elif res['status'] == 'error':
            print(res['err-code'] + ":" + res['err-msg'])
            return False


def get_margin_orders(exchange='huobipro', symbol='btcusdt', currency='btc', start_date="", end_date="", start="", direct="", size=0):
    """
    # 借贷订单
    :param symbol:
    :param currency:
    :param direct: prev 向前，next 向后
    :return:
    """
    if exchange == 'huobipro':
        res = hb.loan_orders(symbol=symbol, currency=currency, start_date=start_date, end_date=end_date, start=start, direct=direct, size=str(size))
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
                data_df['strtime'] = [time.strftime('%Y-%m-%d %H:%M:%S', each/1000) for each in data_df['accrued-at']]
                data_df = data_df[data_df['currency'] == currency]
                data_df.sort_values(by='accrued-at', inplace=True)

                return data_df
            else:
                print('No history orders found!')
                return None

        elif res['status'] == 'error':
            print(res['err-code'] + ":" + res['err-msg'])
            return None


def get_margin_balance(exchange, symbol):
    ''''
    '''
    # 借贷账户详情,支持查询单个币种
    if exchange == 'huobipro':
        res = hb.margin_balance(symbol=symbol)
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


def subscribe(symbol_list):
    '''

    :param symbol_list:
    :return:
    '''
    pass


def get_last_ticks(exchange, symbol_list):
    '''

    :param exchange:
    :param symbol_list:
    :return:
    '''

    symbol_list = symbol_list.replace(' ', '').split(',')
    ticks = []
    if exchange == 'huobipro':
        for each in symbol_list:
            tick_res = hb.get_ticker(symbol=each)
            # depth_res = hb.get_depth(symbol=each, type='step5')
            if tick_res['status'] == 'ok':
                data = tick_res['tick']
                tick = Tick()
                tick.exchange = exchange
                tick.sec_id = each
                tick.utc_time = tick_res['ts']
                tick.strtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tick_res['ts']/1000))
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

    return ticks


def get_last_bars(exchange='btcusdt', symbol_list='btcusdt', bar_type='1min'):
    '''

    :param symbol_list:
    :param bar_type: {1min, 5min, 15min, 30min, 60min, 1day, 1mon, 1week, 1year }
    :return:
    '''
    symbol_list = symbol_list.replace(' ', '').split(',')
    bars = []
    if exchange == 'huobipro':

        for each in symbol_list:
            bar_res = hb.get_kline(symbol=each, period=bar_type, size=1)
            if bar_res['status'] == 'ok':
                data = bar_res['data'][0]
                bar = Bar()
                bar.exchange = exchange
                bar.sec_id = each
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
                bar.strendtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(bar_res['ts']/1000))

                bars = bars + [bar]
            else:
                logger.warn('No bar data fetched!')

    return bars


def get_bars(exchange, symbol_list, bar_type, begin_time='', end_time='', size=0):
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
    for each_sec in symbol_list:

        if begin_time != '':
            size = 2000
        res = hb.get_kline(symbol=each_sec, period=bar_type, size=size)
        if res['status'] == 'ok':
            data = res['data']
            for each_bar in data:
                bar = Bar()
                bar.exchange = exchange
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

                bars = bars + [bar]
        else:
            logger.warn(res['err-code'] + ":" + res['error-msg'])

    return bars


def open_long(exchange='huobipro', source='api', sec_id='btcusdt', price=0, volume=0):
    '''
    异步开多仓，以参数指定的symbol、价和量下单。如果价格为0，为市价单，否则为限价单。
    :param exchange: string	交易所代码，如火币网：huobipro，OKCoin: okcoin
    :param source: string   订单接口源，api：普通订单，margin-api：融资融券订单
    :param sec_id: string   证券代码
    :param price: float     委托价，如果price=0,为市价单，否则为限价单
    :param volume: float	委托量
    :return: 委托下单生成的Order对象
    '''

    myorder = Order()
    myorder.exchange = exchange
    myorder.sec_id = sec_id
    myorder.price = price                ## 委托价
    myorder.volume = volume              ## 委托量
    myorder.cl_ord_id = ''

    myorder.position_effect = 1          ## 开平标志，1：开仓，2：平仓
    myorder.side = 1                     ## 买卖方向，1：多方向，2：空方向


    if exchange == 'huobipro':         # 火币网接口
        if price == 0.0:
            mtype = 'sell-market'
        else:
            mtype = 'sell-limit'
        myorder.order_type = mtype          ## 订单类型
        myorder.order_src = source  ## 订单来源

        # 买入指定数字货币
        myorder.sending_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        if source == 'api':
            result = hb.send_order(amount=volume, source=source, symbol=sec_id, _type=mtype, price=price)
        elif source == 'margin-api':
            result = hb.send_margin_order(amount=volume, source=source, symbol=sec_id, _type=mtype, price=price)

        if result['status'] == 'ok':
            myorder.ex_ord_id = result['data']

            time.sleep(2) # 等待3 秒后查询订单
            # 查询订单信息
            order_info = hb.order_info(myorder.ex_ord_id)
            myorder.account_id = order_info['data']['account-id']
            myorder.status = order_info['data']['state']
            myorder.sending_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(order_info['data']['created-at']/1000))
            myorder.filled_volume = float(order_info['data']['field-amount'])  ## 已成交量
            myorder.filled_amount = float(order_info['data']['field-cash-amount'])  ## 已成交额
            if (myorder.filled_volume > 0):
                myorder.filled_vwap = round(myorder.filled_amount/myorder.filled_volume,4)  ## 已成交均价
            myorder.filled_fee = float(order_info['data']['field-fees'])  ## 手续费
            myorder.transact_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(order_info['data']['finished-at']/1000))  ## 最新一次成交时间

            logger.info('%s 订单号 %s：%s 开多仓，成交量 = %f，成交均价 = %f，总成交额 = %f，手续费 = %f。' % \
                        (myorder.exchange, myorder.ex_ord_id, myorder.sec_id, myorder.filled_volume, myorder.filled_vwap, myorder.filled_amount, myorder.filled_fee))

        elif result['status'] == 'error':
            myorder.status = result['status']
            myorder.ord_rej_reason = result['err-code']  ## 订单拒绝原因
            myorder.ord_rej_reason_detail = result['err-msg']  ## 订单拒绝原因描述
            logger.warn('%s 订单号 %s：%s 开多仓 %f 失败，失败编码：%s，具体原因：%s。' % \
                        (myorder.exchange, myorder.ex_ord_id, myorder.sec_id, myorder.volume, myorder.ord_rej_reason, myorder.ord_rej_reason_detail))

        return myorder


def close_long(exchange, source, sec_id, price, volume):
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
    myorder.exchange = exchange
    myorder.sec_id = sec_id
    myorder.price = price                ## 委托价
    myorder.volume = volume              ## 委托量
    myorder.cl_ord_id = ''

    myorder.position_effect = 2          ## 开平标志，1：开仓，2：平仓
    myorder.side = 1                     ## 买卖方向，1：多方向，2：空方向
    myorder.order_type = 0               ## 订单类型
    myorder.order_src = 0                ## 订单来源

    if exchange == 'huobipro':         # 火币网接口

        if price == 0.0:
            mtype = 'sell-market'
        else:
            mtype = 'sell-limit'

        myorder.sending_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

        if source == 'api':
            result = hb.send_order(amount=volume, source=source, symbol=sec_id, _type=mtype, price=price)
        elif source == 'margin-api':
            result = hb.send_margin_order(amount=volume, source=source, symbol=sec_id, _type=mtype, price=price)

        if result['status'] == 'ok':
            myorder.ex_ord_id = result['data']

            time.sleep(2)  # 等待3 秒后查询订单
            # 查询订单信息
            order_info = hb.order_info(myorder.ex_ord_id)
            myorder.status = order_info['data']['state']
            myorder.account_id = order_info['data']['account-id']
            myorder.sending_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(order_info['data']['created-at']/1000))
            myorder.filled_volume = float(order_info['data']['field-amount'])  ## 已成交量
            myorder.filled_amount = float(order_info['data']['field-cash-amount'])  ## 已成交额
            if (myorder.filled_volume > 0):
                myorder.filled_vwap = round(myorder.filled_amount/myorder.filled_volume,4)  ## 已成交均价
            myorder.filled_fee = float(order_info['data']['field-fees'])  ## 已成交额
            myorder.transact_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(order_info['data']['finished-at']/1000))  ## 最新一次成交时间
            logger.info('%s 订单号 %s：%s 平多仓，成交量 = %f，成交均价 = %f，总成交额 = %f，手续费 = %f。' % \
                        (myorder.exchange, myorder.ex_ord_id, myorder.sec_id, myorder.filled_volume, myorder.filled_vwap, myorder.filled_amount, myorder.filled_fee))

        elif result['status'] == 'error':
            myorder.status = result['status']
            myorder.ord_rej_reason = result['err-code']  ## 订单拒绝原因
            myorder.ord_rej_reason_detail = result['err-msg']  ## 订单拒绝原因描述
            logger.warn('%s 订单号 %s：%s 平多仓 %f 失败，失败编码：%s，具体原因：%s。' % \
                        (myorder.exchange, myorder.ex_ord_id, myorder.sec_id, myorder.volume, myorder.ord_rej_reason, myorder.ord_rej_reason_detail))

        return myorder


def margincash_open(exchange='huobipro', sec_id='btcusdt', price=0, volume=0, leverage=0):
    '''
    融资买入
    :param exchange:
    :param sec_id:
    :param price:
    :param volume: 本金数量
    :param leverage: 杠杆比例
    :return: Order 对象
    '''

    # 第一步：先融资
    margin_currency = 'usdt'
    margin_amount = volume * leverage
    margin_order_id = get_margin(exchange=exchange, symbol=sec_id, currency=margin_currency, amount=margin_amount)

    # 第二步：买入数字货币
    buy_amount = volume + margin_amount
    myorder = open_long(exchange=exchange, source='magin-api', sec_id=sec_id, price=price, volume=buy_amount)

    myorder.margin_amount = margin_amount
    myorder.margin_currency = margin_currency
    myorder.margin_order_id = margin_order_id

    return myorder


def margincash_close(exchange='huobipro', sec_id='btcusdt', price=0, volume=0):
    '''
    融资买入
    :param exchange:
    :param sec_id:
    :param price:
    :param volume:
    :return:
    '''

    # 第一步：先卖出数字货币
    close_order = close_long(exchange=exchange, source= 'margin-api', sec_id=sec_id, price=price, volume=volume)

    # 第二步：归还USDT
    # 获取待还金额
    currency = 'usdt'
    today = time.strftime('%Y-%m-%d', time.localtime())
    margin_orders = get_margin_orders(exchange=exchange, symbol=sec_id, currency=currency, start=today, direct="prev", size=10)
    unpaid_orders = margin_orders[(margin_orders['currency'] == currency) & (margin_orders['state'] == 'accrual')]
    margin_order_id = unpaid_orders.iloc[-1]['id']
    unpaid_volume = unpaid_orders.iloc[-1]['loan-amount'] + unpaid_orders.iloc[-1]['interest-amount']
    if volume < unpaid_volume:
        paid_volume = volume
    else:
        paid_volume = unpaid_volume

    # 偿还借贷
    repay_status = repay_margin(exchange=exchange, margin_order_id=margin_order_id, amount=paid_volume)
    close_order.margin_order_id = margin_order_id
    close_order.margin_currency = currency
    close_order.margin_amount = -paid_volume

    return close_order


def marginsec_open(exchange='huobipro', sec_id='btcusdt', price=0, volume=0):
    '''
    融券做空
    :param exchange: 交易所
    :param sec_id: 证券代码
    :param price: 委托价格，price=0 为市价
    :param volume: 委托数量
    :return:
    '''

    # 第一步，先借入数字货币
    margin_order_id = get_margin(exchange=exchange, symbol=sec_id, currency='btc', amount=volume)

    # 第二步，卖出数字货币
    short_order_id = close_long(exchange=exchange, source='margin-api', sec_id=sec_id, price=price, volume=volume)

    return margin_order_id


def marginsec_close(exchange='huobipro', sec_id='btcusdt', price=0, volume=0):
    '''
    卖券归还
    :param exchange:
    :param sec_id:
    :param price:
    :param volume:
    :return:
    '''

    # 第一步：先买入数字货币
    myorder = open_long(exchange=exchange, source='margin-api', sec_id=sec_id, price=price, volume=volume)

    # 第二步：归还数字货币
    # 获取待还金额
    currency = 'btc'
    today = time.strftime('%Y-%m-%d', time.localtime())
    margin_orders = get_margin_orders(exchange=exchange, symbol=sec_id, currency=currency, start=today, direct="prev", size=10)
    unpaid_orders = margin_orders[(margin_orders['currency'] == currency) & (margin_orders['state'] == 'accrual')]
    margin_order_id = unpaid_orders.iloc[-1]['id']
    unpaid_volume = unpaid_orders.iloc[-1]['loan-amount'] + unpaid_orders.iloc[-1]['interest-amount']

    if volume < unpaid_volume:
        paid_volume = volume
    else:
        paid_volume = unpaid_volume

    repay_status = repay_margin(exchange=exchange, margin_order_id=margin_order_id, amount=paid_volume)
    myorder.margin_order_id = margin_order_id
    myorder.margin_currency = currency
    myorder.margin_amount = -paid_volume

    logger.info('%s 订单号 %s：%s 融券平空仓，成交量 = %f，成交均价 = %f，总成交额 = %f，手续费 = %f。' % \
                (myorder.exchange, myorder.ex_ord_id, myorder.sec_id, myorder.filled_volume, myorder.filled_vwap,
                 myorder.filled_amount, myorder.filled_fee))

    return myorder


def get_position(exchange, sec_id, side):
    '''

    :param exchange:
    :param sec_id:
    :param side:
    :return:
    '''
    pass


def get_positions(exchange='huobipro'):
    '''

    :param exchange:
    :return:
    '''

    positions = []
    if exchange == 'huobipro':

        accounts = get_accounts(exchange=exchange)

        # 获取普通账户资金情况
        spot_account = accounts['spot']['id']
        res = hb.get_balance(acct_id=spot_account)
        if res['status'] == 'ok':
            account_info = res['data']
            account_id = account_info['id']
            account_type = account_info['type']
            account_status = account_info['state']
            account_balance = account_info['list']

            data_df = pd.DataFrame(data=account_balance)
            data_df.index = data_df['currency']
            data_new = pd.DataFrame([], index=np.unique(data_df['currency']), columns=['trade', 'frozen', 'loan', 'interest'])
            data_new['trade'] = data_df[data_df['type']=='trade']['balance']
            data_new['frozen'] = data_df[data_df['type'] == 'frozen']['balance']
            data_new['loan'] = data_df[data_df['type'] == 'loan']['balance']
            data_new['interest'] = data_df[data_df['type'] == 'interest']['balance']
            data_new = data_new.astype('float')
            tmp = data_new.apply(lambda x: sum(np.abs(x)), axis=1)
            data_selected = data_new.loc[tmp[tmp>0].index]

            for each in data_selected.index:
                position = Position()
                position.exchange = exchange
                position.account_id = account_id
                position.account_type = account_type
                position.account_status = account_status

                position.sec_id = each
                position.available = float(data_selected.loc[each]['trade'])
                position.order_frozen = float(data_selected.loc[each]['frozen'])
                position.amount = position.available + position.order_frozen
                position.loan = data_selected.loc[each]['loan']
                position.interest = data_selected.loc[each]['interest']

                positions = positions + [position]
        else:
            logger.warn(res['err-code'] + ':' + res['err-msg'])

    return positions


def get_margin_positions(exchange='huobipro'):
    '''

    :param exchange:
    :return:
    '''

    positions = []
    if exchange == 'huobipro':

        accounts = get_accounts(exchange=exchange)

        # 获取普通账户资金情况
        spot_account = accounts['spot']['id']
        res = hb.get_balance(acct_id=spot_account)
        if res['status'] == 'ok':
            account_info = res['data']
            account_id = account_info['id']
            account_type = account_info['type']
            account_status = account_info['state']
            account_balance = account_info['list']

            data_df = pd.DataFrame(data=account_balance)
            data_df.index = data_df['currency']
            data_new = pd.DataFrame([], index=np.unique(data_df['currency']), columns=['trade', 'frozen', 'loan', 'interest'])
            data_new['trade'] = data_df[data_df['type']=='trade']['balance']
            data_new['frozen'] = data_df[data_df['type'] == 'frozen']['balance']
            data_new['loan'] = data_df[data_df['type'] == 'loan']['balance']
            data_new['interest'] = data_df[data_df['type'] == 'interest']['balance']
            data_new = data_new.astype('float')
            tmp = data_new.apply(lambda x: sum(np.abs(x)), axis=1)
            data_selected = data_new.loc[tmp[tmp>0].index]

            for each in data_selected.index:
                position = Position()
                position.exchange = exchange
                position.account_id = account_id
                position.account_type = account_type
                position.account_status = account_status

                position.sec_id = each
                position.available = float(data_selected.loc[each]['trade'])
                position.order_frozen = float(data_selected.loc[each]['frozen'])
                position.amount = position.available + position.order_frozen
                position.loan = data_selected.loc[each]['loan']
                position.interest = data_selected.loc[each]['interest']

                positions = positions + [position]
        else:
            logger.warn(res['err-code'] + ':' + res['err-msg'])

    return positions


def get_cash():
    '''

    :return:
    '''
    pass


def send_order(exchange='huobipro', symbol='btcusdt', amount=0, margin=0, mtype='buy-market', price=0):
    '''
    发送交易订单
    :param ex:
    :param symbol: 交易品种代码
    :param amount: 限价单表示下单数量，市价买单时表示买多少钱，市价卖单时表示卖多少币
    :param margin: 如果使用借贷资产交易，margin=1
    :param mtype: 可选值 {buy-market：市价买, sell-market：市价卖, buy-limit：限价买, sell-limit：限价卖}
    :param price: 如果限价单，指定价格。市价单无须指定
    :return:
    '''

    if ex=='huobipro':
        if margin == 1 :
            margin_order = 'margin_api'
        else:
            margin_order = None
            result = hb.send_order(amount=amount, source=margin_order, symbol=symbol, _type=mtype, price=price)
            if result['status'] == 'ok':
                return result['data']
            elif result['status']== 'error':
                print(result['err-code'] + ":" + result['err-msg'])
                return None


def cancel_order(exchange, cl_ord_id=None):
    '''
    取消订单
    :param exchange: 交易所
    :param order_id: 订单号
    :return:
    '''

    if exchange == 'huobipro':
        res = hb.cancel_order(order_id=cl_ord_id)
        if res['status'] == 'ok':
            return res['data']
        else:
            logger.warn(res['err-code'] + ':' + res['err-msg'])
            return None


def get_order(exchange, cl_ord_id):
    '''
    获取历史订单信息
    :param cl_ord_id:
    :return:
    '''

    if exchange == 'huobipro':
        res = hb.order_info(cl_ord_id)
        if res['status'] == 'ok':
            data = res['data']
            order = Order()
            order.exchange      = exchange
            order.account_id    = data['account-id']
            order.cl_ord_id     = cl_ord_id
            order.order_id      = data['id']
            order.order_src     = data['source']
            order.status        = data['state']
            order.sec_id        = data['symbol']
            order.order_type    = data['type']
            order.side          = data['type']
            order.position_effect = data['type']
            order.sending_time  = data['created-at']
            order.transact_time = data['finished-at']
            order.volume        = float(data['amount'])
            order.price         = float(data['price'])
            order.filled_amount = float(data['field-cash-amount'])
            order.filled_fee = float(data['field-fees'])
            order.filled_volume = float(data['field-amount'])
            if (order.filled_volume > 0):
                order.filled_vwap = round(order.filled_amount/order.filled_volume,4)  ## 已成交均价

            return order
        else:
            logger.warn(res['err-code'] + ":" + res['err-msg'])
            return None


def get_orders_by_symbol(exchange, sec_id, start_time, end_time, states='filled', types=None):
    '''

    :param exchange:
    :param sec_id:
    :param states: 查询的订单状态组合，使用','分割。pre-submitted 准备提交, submitted 已提交, partial-filled 部分成交, partial-canceled 部分成交撤销, filled 完全成交, canceled 已撤销
    :param types:  查询的订单类型组合，使用','分割。buy-market：市价买, sell-market：市价卖, buy-limit：限价买, sell-limit：限价卖
    :param start_time:
    :param end_time:
    :return:
    '''
    if states == 'all':
        states = 'pre-submitted,submitted,partial-filled,partial-canceled,filled,canceled'
    if types == 'all':
        types = 'buy-market,sell-market,buy-limit,sell-limit'

    orders = []
    if exchange == 'huobipro':

        start_date = time.strftime('%Y-%m-%d', time.strptime(start_time, '%Y-%m-%d %H:%M:%S'))
        end_date = time.strftime('%Y-%m-%d', time.strptime(end_time, '%Y-%m-%d %H:%M:%S'))
        res = hb.orders_list(symbol=sec_id, states=states, types=types, start_date=start_date, end_date=end_date)
        if res['status'] == 'ok':
            data = res['data']

            for each in data:
                order = Order()
                order.exchange = exchange
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
                    order.filled_vwap = round(order.filled_amount/order.filled_volume,4)  ## 已成交均价

                orders = orders + [order]
        else:
            logger.warn(res['err-code'] + ':' + res['err-msg'])

    return orders


