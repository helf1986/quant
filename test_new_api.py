
# 从api接口导入TradeAccount 交易类
from api.quant_api import TradeAccount, to_dataframe, to_dict, get_bars_local
from common.settings import HBP_ACCESS_KEY, HBP_SECRET_KEY, BNB_ACCESS_KEY, BNB_SECRET_KEY
import time
import pandas as pd
from api import logger

'''
from api.quant_api import TradeAccount, to_dataframe, to_dict, get_bars_local
bars = get_bars_local(exchange='hbp', symbol_list='btcusdt', bar_type='5min', size=20)
print(to_dataframe(bars))
'''

# 创建火币交易账户
hbaccount = TradeAccount(exchange='hbp', api_key=HBP_ACCESS_KEY, api_secret=HBP_SECRET_KEY, currency='USDT')

symbol_list = ['bchusdt', 'btcusdt', 'ethusdt', 'xrpusdt','ltcusdt', 'dashusdt', 'iotausdt', 'omgusdt', 'adausdt']

depth_df = pd.DataFrame([], columns=['bid_price', 'bid_amount', 'ask_price', 'ask_amount', 'strtime', 'symbol'])
for each_symbol in symbol_list:
    depth_data = hbaccount.get_depth(symbol=each_symbol, type='step0')
    print(depth_data.head())
    depth_df = depth_df.append(depth_data)

print(len(depth_df))
depth_df.to_csv('btc_depth.csv')




'''
symbol_list = ['bchusdt', 'btcusdt', 'ethusdt', 'xrpusdt','ltcusdt', 'dashusdt', 'iotausdt', 'omgusdt', 'adausdt']
symbol_str = ','.join(symbol_list)
print(symbol_str)
bars = hbaccount.get_bars(symbol_list=symbol_str, bar_type='1day', size=2000)
bar_df = to_dataframe(bars)
print(bar_df.head())
bar_df.to_csv('bar_1day.csv')
'''



'''
orders = hbaccount.get_orders_by_symbol (sec_id='btcusdt', begin_time='2018-05-06 00:00:00', end_time='2018-05-12 00:00:00', states='filled', types='sell-market')

from common.settings import HBP_ACCESS_KEY, HBP_SECRET_KEY, BNB_ACCESS_KEY, BNB_SECRET_KEY
from common.HuobiClient import HuobiClient
client = HuobiClient(api_key=HBP_ACCESS_KEY, api_secret=HBP_SECRET_KEY)
res = client.orders_list(symbol='btcusdt', states='filled', types='sell-market', start_date='2018-05-06', end_date='2018-05-12')

res = client.get_depth(symbol='btcusdt', type='step0')




flag = 0
count = 0
while (flag == 0 and count < 10):
    # 允许最多重连10次
    try:
        bars = hbaccount.get_last_bars(symbol_list='btcusdt', bar_type='1min')
        flag = 1
    except Exception as e:
        logger.warn('Connection Failed: ', e)
        count = count + 1
        time.sleep(5)

if flag == 1:
    print(bars)
    # 请继续编写和bars相关的处理算法

'''
'''

time.sleep(1)
bars = hbaccount.get_bars(symbol_list='btcusdt', bar_type='1min', size=2000)
print(len(bars))

bars = get_bars_local(exchange='hbp', symbol_list='btcusdt', bar_type='1min', size=20)
print(len(bars))
'''

'''
# 通过账户访问行情数据
bars = hbaccount.get_last_bars(symbol_list='btcusdt', bar_type='1min')
bars_dict = to_dict(bars[0])
print(bars_dict)
bars_df = to_dataframe(bars)
print(bars_df)


last_price = bars[0].close
print(last_price)
order = hbaccount.open_long(source='margin', sec_id='btcusdt', price=last_price, volume=0.001)
print(to_dict(order))
'''


'''
time.sleep(1)
bars = hbaccount.get_bars(symbol_list='btcusdt', bar_type='1min', size=30)
bars_dict = to_dict(bars[0])
bars_df = to_dataframe(bars)
print(bars_df)

time.sleep(1)
bars = hbaccount.get_bars(symbol_list='ethusdt', bar_type='1min', size=30)
bars_dict = to_dict(bars[0])
bars_df = to_dataframe(bars)
print(bars_df)

time.sleep(1)
bars = hbaccount.get_bars(symbol_list='bchusdt', bar_type='1min', size=30)
bars_dict = to_dict(bars[0])
bars_df = to_dataframe(bars)
print(bars_df)

ticks = hbaccount.get_last_ticks(symbol_list='btcusdt, ethusdt')
ticks_dict = to_dict(ticks[0])
ticks_df = to_dataframe(ticks)
print(ticks_df)

symbols = hbaccount.get_instruments()
symbols_df = to_dataframe(symbols)
symbols_df.to_csv('huobi_symbols.csv')

accounts = hbaccount.get_accounts()
print(accounts)

account_id = accounts['margin']['id']
balance = hbaccount.get_positions(source='margin')

order = hbaccount.open_long(source='margin', sec_id='btcusdt', price=0, volume=0.001)
print(to_dict(order))


order2 = hbaccount.close_long(source='margin', sec_id='btcusdt', price=0, volume=0.001)
print(to_dict(order2))


order3 = hbaccount.apply_margin(symbol='btcusdt', currency='usdt', amount=100)
print(order3)

'''

'''
import time
now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
hbaccount.get_margin_orders(symbol='btcusdt', currency='btc', start=now, direct='prev', size=100)

unpaid_amount = hbaccount.get_margin_volume(margin_order_id=942857, symbol='btcusdt', currency='btc')
result = hbaccount.repay_margin(order_id=942857, amount=unpaid_amount)


## 直接测试火币原始接口
import common.HuobiClient as hb
api_key = HBP_ACCESS_KEY
api_secret = HBP_SECRET_KEY
client = hb.HuobiClient(api_key, api_secret)
res = client.get_kline(symbol='btcusdt', period='1min', size=2)
# 大写输入不行
res = client.get_kline(symbol='BTCUSDT', period='1min', size=2)

res = client.get_symbols()
res = client.get_accounts()

# 创建币安交易账户
bnbaccount = TradeAccount(exchange='bnb', api_key=BNB_ACCESS_KEY, api_secret=BNB_SECRET_KEY, currency='USDT')
bars = bnbaccount.get_last_bars(symbol_list='BTCUSDT', bar_type='5min')
# 通过账户访问行情数据
bars_dict = to_dict(bars[0])
bars_df = to_dataframe(bars)



from common.BinanceClient import BinanceClient
import time
endTime = time.mktime(time.localtime())
startTime = endTime - 60

myacc = BinanceClient(api_key=BNB_ACCESS_KEY, api_secret=BNB_SECRET_KEY)
bars  = myacc.get_klines(symbol='BTCUSDT', interval='1m', startTime=int(startTime*1000), endTime=int(endTime*1000))
'''