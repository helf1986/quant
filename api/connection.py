from pymongo import MongoClient
from api.quant_api import *
import time
from common.settings import MONGO_IP, MONGO_PORT, MONGO_PWD, MONGO_USER

def connect_mongo(ip=None, port=None, dbname=None, user=None, password=None):
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
    db = client[dbname]
    if user and password:
        connected = db.authenticate(user, password)
    else:
        connected = True

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

    # 写入mongodb 数据库
    try:
        client = connect_mongo()
        dbbtcaccount = client['dbbtcaccount']
        # dbbtcaccount.authenticate(MONGO_USER, MONGO_PWD)
        tbtradeorder = dbbtcaccount['tbtradeorder']
        tbtradeorder.insert_one(data)
        return True

    except Exception as e:
        logger.warn('交易订单插入数据库失败！')
        return False


def marginorder2db(margin_order):
    '''
    把融资融券订单写到数据库中，数据表名：tbmarginorder
    :param margin_order:
    :return:
    '''

    # 字典格式转换
    data = {}
    margin_order = MarginOrder()
    data['usr'] = margin_order.account_id
    data['sch'] = margin_order.strategy_id
    data['cur'] = margin_order.currency
    data['exg'] = margin_order.exchange
    data['usrex'] = margin_order.user_id
    data['ordid'] = margin_order.margin_order_id
    data['ordtime'] = margin_order.sending_time
    data['sym'] = margin_order.margin_symbol
    data['marcur'] = margin_order.margin_currency
    data['vol'] = margin_order.margin_volume
    data['filltime'] = margin_order.filled_time
    data['fillvol'] = margin_order.filled_volume
    data['unpvol'] = margin_order.unpaid_volume
    data['interest'] = margin_order.total_interest
    data['unpint'] = margin_order.unpaid_interest
    data['status'] = margin_order.status

    # 写入mongodb 数据库
    try:
        client = connect_mongo()
        dbbtcaccount = client['dbbtcaccount']
        # dbbtcaccount.authenticate(MONGO_USER, MONGO_PWD)
        tbtradeorder = dbbtcaccount['tbmarginorder']
        tbtradeorder.insert_one(data)
        return True

    except Exception as e:
        logger.warn('融资融券订单插入数据库失败！')
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

    try:
        # 把持仓数据写入数据库
        client = connect_mongo()
        dbaccount = client['dbbtcaccount']
        # dbaccount.authenticate(MONGO_USER, MONGO_PWD)
        tbposition = dbaccount['tbposition']
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
        logger.warn('系统日志插入数据库失败！')
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
        logger.warn('交易日志插入数据库失败！')
        return False

def monitor2db(strategy_name=None):
    import json
    f = open("monitor/"+strategy_name+".json", encoding='utf-8')
    info = json.load(f)

    order = Order()

