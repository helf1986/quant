
from api.quant_api import TradeAccount, to_dataframe, to_dict

# 此处填写APIKEY

HBP_ACCESS_KEY = "a4594cdd-75b0037b-003d37ea-528bd"
HBP_SECRET_KEY = "5f0ea6d5-a4ff1afc-9c04e15a-9e3ba"

BNB_ACCESS_KEY = "ayeGIEt9ojK3qhWcYNWrm4QZnDPzDqOdRObg4FaBSMrupw7X6j8e2nwS9x62gbJZ"
BNB_SECRET_KEY = "mfz7XH3KpSg1q5Ag8aVJOP8Lh9vlFYEqURqfCH3NfRLuh3siTvv2yMkAyNQ9B4YA"

hbaccount = TradeAccount(exchange='hbp', api_key=HBP_ACCESS_KEY, api_secret=HBP_SECRET_KEY, currency='USDT')

bars = hbaccount.get_last_bars(symbol_list='btcusdt, ethusdt', bar_type='5min')
bars_dict = to_dict(bars[0])
bars_df = to_dataframe(bars)

bnbaccount = TradeAccount(exchange='bnb', api_key=BNB_ACCESS_KEY, api_secret=BNB_SECRET_KEY, currency='USDT')

bars = bnbaccount.get_last_bars(symbol_list='BTCUSDT', bar_type='5min')
bars_dict = to_dict(bars[0])
bars_df = to_dataframe(bars)



from common.BinanceClient import BinanceClient
import time
endTime = time.mktime(time.localtime())
startTime = endTime - 60

myacc = BinanceClient(api_key=BNB_ACCESS_KEY, api_secret=BNB_SECRET_KEY)
bars  = myacc.get_klines(symbol='BTCUSDT', interval='1m', startTime=int(startTime*1000), endTime=int(endTime*1000))
