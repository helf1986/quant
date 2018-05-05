
# 从api接口导入TradeAccount 交易类
from api.quant_api import TradeAccount, to_dataframe, to_dict
from common.settings import HBP_ACCESS_KEY, HBP_SECRET_KEY, BNB_ACCESS_KEY, BNB_SECRET_KEY

# 创建火币交易账户
hbaccount = TradeAccount(exchange='hbp', api_key=HBP_ACCESS_KEY, api_secret=HBP_SECRET_KEY, currency='USDT')
# 通过账户访问行情数据
bars = hbaccount.get_last_bars(symbol_list='btcusdt, ethusdt', bar_type='1min')
bars_dict = to_dict(bars[0])
bars_df = to_dataframe(bars)


import common.HuobiClient as hb
api_key = HBP_ACCESS_KEY
api_secret = HBP_SECRET_KEY
client = hb.HuobiClient(api_key, api_secret)
res = client.get_kline(symbol='btcusdt', period='1min', size=2)

res = client.get_kline(symbol='BTCUSDT', period='1min', size=2)

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
