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


