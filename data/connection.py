from pymongo import MongoClient

MONGO_IP    = 'localhost'
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
    client = connect_mongo()

def position2db(position):
    '''
    把持仓记录写入到数据库，数据表名：tbposition
    :param position:
    :return:
    '''

    client = connect_mongo()

def perform2db(perform):
    '''
    把业绩表现写入到数据库中，数据表名：tbperform
    :param perform:
    :return:
    '''
    client = connect_mongo()


def syslog2db(syslog):
    '''
    系统日志写入数据库中，数据表名：tbsyslog
    :param syslog:
    :return:
    '''

    client = connect_mongo()





