import api.quant_api as qapi
import common.HuobiServices as hb
import pandas as pd
import time

import matplotlib.pyplot as plt
import common.Utils as ut


if __name__ == "__main__":

    '''
    tick_data = qapi.get_kline('btcusdt', '1min', size=2000)
    keys = range(len(tick_data['data']))
    tick_df = pd.DataFrame.from_dict(dict(zip(keys, tick_data['data'])), orient='index')
    tick_df.index = [time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tmp)) for tmp in tick_df['id']]
    print(tick_df.head())
    '''

    '''
    tick_data = qapi.get_tick(ex='huobi', code='btcusdt')
    print(tick_data)
    '''


    # print(qapi.get_codes().head())

    '''
    myacount = qapi.get_accounts()['id']
    mybalance = qapi.get_balance(acct_id=myacount)
    print(mybalance)
        '''

    '''
    code = 'xrpusdt'
    currency = 'usdt'
    amount = 1
    result = qapi.get_margin(ex='huobi', code=code, currency=currency, amount=amount)
    print(result)
    '''

    '''

    myacount = qapi.get_accounts()['id']
    mybalance = qapi.get_balance(acct_id=myacount)
    # print(mybalance.iloc[0])
    mybalance = mybalance[mybalance['trade'] > 0]
    print(mybalance)

    if (len(mybalance) > 0):

        code = 'btcusdt'
        amount = round(mybalance.loc['usdt']['trade']*0.1, 4)
        direction = 1       # 1: 多头，-1：空头，0：平仓
        # 获取市场价格
        tick_data = qapi.get_tick(symbol=code)
        # 按照市价下单
        price = 0
        if direction == 1:
            order_id = qapi.open_long(exchange='huobi', sec_id=code, price=price, volume=amount)

        elif direction == -1:
            order_id = qapi.close_long(exchange='huobi', sec_id=code, price=price, volume=amount)
        
    '''
    '''
        data = qapi.get_orders(exchange='huobipro', sec_id='btcusdt', start_time='2018-03-27 00:00:01', end_time='2018-03-29 23:59:59')

    print(data)



    data = qapi.get_last_ticks(exchange='huobipro', symbol_list=['btcusdt', 'ethusdt'])

    for each in data:
        print (each.sec_id, each.last_price)

    '''

    # res = qapi.open_short(exchange='huobipro', sec_id='btcusdt', price=0, volume=0.001)

    # result = hb.send_margin_order(amount=0.001, source='margin-api', symbol='btcusdt', _type='sell-market', price=0)

    # result = qapi.close_short(exchange='huobipro', sec_id='btcusdt', price=0, volume=1)
    # result = qapi.open_long(exchange='huobipro', sec_id='btcusdt', price=0, volume=1)

    # result = qapi.get_positions(exchange='huobipro')

    '''

    result = qapi.get_bars(exchange='huobipro', symbol_list=['btcusdt', 'ethusdt'], bar_type='1min', begin_time='', end_time='', size=50)
    result_dict = [each.__dict__ for each in result]
    result_pd = pd.DataFrame(result_dict)
    print(result_pd)
        '''

    data = qapi.get_bars_local(exchange='huobipro', symbol_list='btcusdt', bar_type='5min', size=100)
    data_df = qapi.to_dataframe(data)
    print(data_df)

    myorder = qapi.open_long(exchange='huobipro', source='margin-api', sec_id='btcusdt', price=0, volume=0.001)

    myorder = qapi.close_long(exchange='huobipro', source='margin-api', sec_id='btcusdt', price=0, volume=0.002)

    margin_orders = qapi.get_margin_orders(exchange='huobipro', symbol='btcusdt', currency='btc', start="2018-04-06", direct="prev", size=10)

    result = qapi.apply_margin(exchange='huobipro', symbol='btcusdt', currency='btc', amount=0.001)

    result = qapi.apply_margin(exchange='huobipro', symbol='btcusdt', currency='usdt', amount=0.001)

    result = qapi.repay_margin(exchange='huobipro', order_id=676027, amount=0.15)

    myaccount = qapi.get_positions(exchange='huobipro')


    myorder = qapi.margincash_open(exchange='huobipro', sec_id='btcusdt', price=0, volume=0.01, leverage=1)

    myorder = qapi.margincash_close(exchange='huobipro', sec_id='btcusdt', price=0, volume=0.02)

    myorder = qapi.marginsec_open(exchange='huobipro', sec_id='btcusdt', price=0, volume=0.001)

    last_tick = qapi.get_last_ticks(exchange='huobipro', symbol_list='btcusdt')
    last_price = last_tick[0].last_price
    result= qapi.marginsec_close(exchange='huobipro', sec_id='btcusdt', price=last_price, volume=0.001)

    last_tick = qapi.get_last_ticks(exchange='huobipro', symbol_list='btcusdt')
    last_price = last_tick[0].last_price
