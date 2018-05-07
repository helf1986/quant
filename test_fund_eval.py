
from common.settings import HBP_SECRET_KEY, HBP_ACCESS_KEY
from api.quant_api import TradeAccount, to_dataframe, to_dict, get_bars_local, Indicator, Tick, Order, Bar
import time
import pandas as pd
import numpy as np
import api.connection as conn
from api.fund_perform_eval import PerformEval


def tradelog(account=None):

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
            netvalue = to_dataframe(hist_position)
            myindicator = Indicator()
            perform = PerformEval(netvalue)


if __name__ == '__main__':

    hbaccount = TradeAccount(exchange='hbp', api_key=HBP_ACCESS_KEY,api_secret=HBP_SECRET_KEY, currency='USDT')

    posistions = hbaccount.get_positions(source='margin')
    total_amount = 0
    currency = hbaccount.currency.lower()
    for each_pos in posistions:
        sec_id = each_pos.sec_id.lower()
        if sec_id != currency:
            symbol = sec_id + currency
            print(symbol)
            tick = hbaccount.get_last_ticks(symbol_list=symbol)
            tick = Tick()
            total_amount = total_amount + each_pos.amount*tick.last_price
        else:
            total_amount = total_amount + each_pos.amount

    print(total_amount)