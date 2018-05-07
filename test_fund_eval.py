
from common.settings import HBP_SECRET_KEY, HBP_ACCESS_KEY
import api.quant_api as qapi
import time
import pandas as pd
import numpy as np
import api.connection as conn
from api.fund_perform_eval import PerformEval


def tradelog(account=None):

    account = qapi.TradeAccount()
    account.get_orders_by_symbol(sec_id = 'btcusdt')


def clearing(account=None, interval='1day', ctime='00:00:00'):
    '''
    定期进行清结算
    :param interval: 支持两种方式，interval='1day' 每天结算一次，interval='60min' 每小时结算一次
    :param ctime: 指定每天具体时间
    :return:
    '''

    while (1):
        isStart = False
        now = time.localtime(time.time())
        if interval == '1day':
            # 每日 00:00:00 进行清算
            if now.tm_hour == 0 and now.tm_min == 0:
                isStart = True
        elif interval == '60min':
            # 每小时清算一次，XX:00:00 进行结算
            if now.tm_min == 0:
                isStart = True

        if isStart:
            positions = account.get_positions(source='margin')
            hist_position = hist_position + [positions]
            netvalue = qapi.to_dataframe(hist_position)
            myindicator = qapi.Indicator()
            perform = PerformEval(netvalue)


if __name__ == '__main__':

    hbaccount = qapi.TradeAccount(exchange='hbp', api_key=HBP_ACCESS_KEY,api_secret=HBP_SECRET_KEY, currency='USDT')

    order_records = []

    position_records = {}

    hbaccount.get_orders_by_symbol()