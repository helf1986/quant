from pymongo import MongoClient
from api.quant_api import *
import time

# MONGO_IP    = 'localhost'
MONGO_IP    =  '47.75.172.148'
MONGO_PORT  = '27017'

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


def order2db(order):
    '''
    把交易订单写到数据库中，数据表名：tbtradeorder
    :param order:
    :return:
    '''

    # 字典格式转换
    data = {}
    data['usr'] = order.account_id
    data['sch'] = order.strategy_id
    data['cur'] = order.currency
    data['exg'] = order.exchange
    data['usrex'] = order.user_id
    data['ordid'] = order.order_id
    data['ordtime'] = order.sending_time
    data['sym'] = order.sec_id
    data['dir'] = order.side
    data['vol'] = order.volume
    data['price'] = order.price
    data['filltime'] = order.transact_time
    data['fillvol'] = order.filled_volume
    data['fillprice'] = order.filled_vwap
    data['fillamt'] = order.filled_amount
    data['fee'] = order.filled_fee
    data['status'] = order.status
    data['mgid'] = order.margin_order_id
    data['mgamt'] = order.margin_amount
    data['mgcur'] = order.margin_currency

    # 写入mongodb 数据库
    try:
        client = connect_mongo()
        dbbtcaccount = client['dbbtcaccount']
        tbtradeorder = dbbtcaccount['tbtradeorder']
        tbtradeorder.insert_one(data)
        return True

    except Exception as e:
        logger.warn('交易数据插入数据库失败！')
        return False


def position2db(positions):
    '''
    把持仓记录写入到数据库，数据表名：tbposition
    :param position: 当前持仓，Position 列表
    :return:
    '''

    # 持仓数据的字典格式转换
    data_list = []
    for each_pos in positions:

        data = {}
        data['usr'] = each_pos.account_id
        data['sch'] = each_pos.strategy_id
        data['cur'] = each_pos.currency
        data['time'] = each_pos.update_time
        data['sym'] = each_pos.sec_id
        data['vol'] = each_pos.volume
        data['price'] = each_pos.price
        data['amt'] = each_pos.amt
        data['loanid'] = each_pos.loan_order_id
        data['loanvol'] = each_pos.loan
        data['interest'] = each_pos.interest

        data_list = data_list + [data]

    # 把持仓数据写入数据库
    client = connect_mongo()
    dbaccount = client['dbbtcaccount']
    tbposition = dbaccount['tbposition']

    try:
        tbposition.insert_many(data_list)
        return True
    except Exception as e:
        logger.warn('持仓数据插入数据库失败！')
        return False


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

    client = connect_mongo()


def syslog2db(syslog):
    '''
    系统日志写入数据库中，数据表名：tbsyslog
    :param syslog:
    :return:
    '''

    data = {}
    data['usr'] = 0
    data['sch'] = 0
    data['time'] = time.strftime('%Y-%d-%m %H:%M:%S', time.localtime(time.time()))
    data['msg'] = syslog

    # 写入mongodb 数据库
    try:
        client = connect_mongo()
        dbbtc = client['dbbtcaccount']
        tbsyslog = dbbtc['tbsyslog']
        tbsyslog.insert_one(data)
        return True

    except Exception as e:
        logger.warn('交易数据插入数据库失败！')
        return False


def tradelog2db(tradelog):
    '''
    交易日志写入数据库中，数据表名：tbtradelog
    :param tradelog:
    :return:
    '''

    data = {}
    data['usr'] = 0
    data['sch'] = 0
    data['time'] = time.strftime('%Y-%d-%m %H:%M:%S', time.localtime(time.time()))
    data['msg'] = tradelog

    # 写入mongodb 数据库
    try:
        client = connect_mongo()
        dbbtc = client['dbbtcaccount']
        tbtradelog = dbbtc['tbtradelog']
        tbtradelog.insert_one(data)
        return True

    except Exception as e:
        logger.warn('交易数据插入数据库失败！')
        return False



