
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
        elif interval == '60min' or interval =='1hour':
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
    currency = hbaccount.currency.lower()

    pos_df = pd.DataFrame([], columns=['spot', 'margin', 'loan'])

    # 普通账户数量
    positions = hbaccount.get_positions(source='spot')
    for each_pos in positions:
        sec_id = each_pos.sec_id.lower()
        if sec_id in pos_df.index:
            pos_df.loc[sec_id, 'spot'] = each_pos.volume
        else:
            each_df = pd.DataFrame([], index=[sec_id], columns=['spot', 'margin', 'loan'])
            each_df.loc[sec_id, 'spot'] = each_pos.volume
            pos_df = pos_df.append(each_df)


    # 借贷账户数量
    positions = hbaccount.get_positions(source='margin')
    for each_pos in positions:
        sec_id = each_pos.sec_id.lower()
        if sec_id in pos_df.index:
            pos_df.loc[sec_id, 'margin'] = each_pos.volume
        else:
            each_df = pd.DataFrame([], index=[sec_id], columns=['spot', 'margin', 'loan'])
            each_df.loc[sec_id, 'margin'] = each_pos.volume
            pos_df = pos_df.append(each_df)

    '''
    # 借贷资产需要扣除
    for each_sec in pos_df.index:
        sec_id = each_sec.lower()
        symbol = sec_id + currency
        loans = hbaccount.get_margin_balance(symbol=symbol)

    '''

    pos_df = pos_df.fillna(0)
    pos_df['volume'] = pos_df['spot'] + pos_df['margin'] - pos_df['loan']
    pos_df['price'] = 0

    # 统计总的持仓
    total_amount = 0
    for each_sec in pos_df.index:
        sec_id = each_sec.lower()
        if sec_id != currency:
            symbol = sec_id + currency
            tick = hbaccount.get_last_ticks(symbol_list=symbol)
            symbol_tick = tick[0]
            print(symbol, symbol_tick.last_price)
            pos_df.loc[each_sec, 'price'] = symbol_tick.last_price
        else:
            pos_df.loc[each_sec, 'price'] = 1

    pos_df['total'] = pos_df['volume']*pos_df['price']
    print(pos_df)
    total_amount = pos_df['total'].sum()
    print(total_amount)