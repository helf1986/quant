from pymongo import MongoClient
import time
import pandas as pd
import numpy as np

from api.fund_perform_eval import PerformEval
# from api.quant_api import get_bars_local
# from api.quant_api import Indicator
# from api.connection import perform2db
from api import logger

'''

client = MongoClient('47.75.69.176', 28005)
coin_db = client['bc_bourse_huobipro']
coin_db.authenticate('helifeng', 'w7UzEd3g6#he6$ahYG')
collection = coin_db['b_bch_kline']

data = collection.find({'per': "3", "ts": {"$gt": "2017-05-01 19:50:00"}})

hist_data = {}
for each in data:
    hist_data[each['ts']] = each

hist_df = pd.DataFrame.from_dict(hist_data, orient='index')
print(hist_df.head())

hist_df.to_csv('bch_20171101_20180501.csv')
'''

from common.settings import MONGO_IP, MONGO_PORT
def connect_mongo(ip=None, port=None):
    '''
    连接mongodb数据库
    :param ip:
    :param port:
    :return:
    '''
    if ip == None:
        ip = MONGO_IP
        port = MONGO_PORT

    client = MongoClient(host=ip, port=port)

    return client


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


def perform2db(indicator):
    '''
    把业绩表现写入到数据库中，数据表名：tbperform
    :param indicator:
    :return:
    '''

    # 字典映射
    data = {}
    data['usr'] = indicator.account_id
    data['sch'] = indicator.strategy_id
    data['cur'] = indicator.currency
    data['time'] = indicator.transact_time
    data['tot'] = indicator.total_amt
    data['nav'] = indicator.nav
    data['navacc'] = indicator.nav
    data['ret'] = indicator.total_return
    data['annret'] = indicator.annual_return
    data['std'] = indicator.risk_ratio
    data['maxdd'] = indicator.max_drawdown
    data['win'] = indicator.win_ratio
    data['sharpe'] = indicator.sharp_ratio
    data['retvsdd'] = indicator.annual_return/indicator.max_drawdown

    try:
        # 把持仓数据写入数据库
        client = connect_mongo()
        dbaccount = client['dbbtcaccount']
        # dbaccount.authenticate(MONGO_USER, MONGO_PWD)
        tbposition = dbaccount['tbperform']
        tbposition.insert_one(data)
        return True
    except Exception as e:
        logger.warn('业绩数据插入数据库失败！')
        return False



data = pd.read_csv('btc_netvalue.csv', index_col=0, header=0)
total_asset = 30000
data['netvalue'] = 1+ data['total_return']/total_asset
data['daily_return'] = data['daily_return']/total_asset
data.index = [time.strftime('%Y-%m-%d', time.strptime(each, '%Y/%m/%d')) for each in data.index]

# benchmark = get_bars_local(exchange='hbp', symbol_list='btcusdt', bar_type='1day', begin_time=data['date'].iloc[0], end_time=data['date'].iloc[-1])

performs = []
for nn in range(1, len(data)):
    netvalue = data['netvalue'].iloc[0:nn+1]
    result = PerformEval(net_value=netvalue, benchmark_value=netvalue, riskfree_rate=0.0, return_type='d')
    each_perform = Indicator()
    each_perform.transact_time = netvalue.index[nn]
    each_perform.currency = 'usdt'
    each_perform.total_amt = data['total_return'].iloc[nn]
    each_perform.daily_return = netvalue.iloc[-1]/netvalue[-2]-1
    each_perform.annual_return = result['annual_return']
    each_perform.max_drawdown = result['max_drawdown']
    each_perform.sharp_ratio = result['sharpe']
    each_perform.total_return = result['total_return']
    each_perform.win_ratio = result['win']
    each_perform.nav = netvalue.iloc[-1]
    each_perform.risk_ratio = each_perform.annual_return/each_perform.max_drawdown

    performs = performs + [each_perform]


for each_perform in performs:
    perform2db(each_perform)

