import numpy as np
import pandas as pd
import os
import time

from common.BinanceClient import BinanceClient
from api import logger

BNB_API_KEY = 'ayeGIEt9ojK3qhWcYNWrm4QZnDPzDqOdRObg4FaBSMrupw7X6j8e2nwS9x62gbJZ'
BNB_SECRET_KEY = 'mfz7XH3KpSg1q5Ag8aVJOP8Lh9vlFYEqURqfCH3NfRLuh3siTvv2yMkAyNQ9B4YA'

mybnb = BinanceClient(api_key= BNB_API_KEY, api_secret= BNB_SECRET_KEY)

print(mybnb.API_KEY)

depth = mybnb.get_order_book(symbol='BNBBTC')
print(depth)

'''

order = mybnb.create_order(
    symbol='BNBBTC',
    side=BinanceClient.SIDE_BUY,
    type=BinanceClient.ORDER_TYPE_MARKET,
    quantity=100)


myaccount = mybnb.get_account()

print (myaccount)


# get market depth
depth = mybnb.get_order_book(symbol='BNBBTC')

# place market buy order
order = mybnb.create_order(
    symbol='BNBBTC',
    side=BinanceClient.SIDE_BUY,
    type=BinanceClient.ORDER_TYPE_MARKET,
    quantity=100)

# get all symbol prices
prices = BinanceClient.get_all_tickers()

# withdraw 100 ETH
# check docs for assumptions around withdrawals
from common.BinanceUtils import BinanceAPIException, BinanceWithdrawException
try:
    result = mybnb.withdraw(
        asset='ETH',
        address='<eth_address>',
        amount=100)
except BinanceAPIException as e:
    print(e)
except BinanceWithdrawException as e:
    print(e)
else:
    print("Success")

# fetch list of withdrawals
withdraws = mybnb.get_withdraw_history()

# fetch list of ETH withdrawals
eth_withdraws = mybnb.get_withdraw_history('ETH')

# get a deposit address
address = mybnb.get_deposit_address('BTC')

# start trade websocket
def process_message(msg):
    print("message type: {}".format(msg['e']))
    print(msg)
    # do something

from common.BinanceClient import BinanceSocketManager
bm = BinanceSocketManager(mybnb)
bm.start_aggtrade_socket(symbol='BNBBTC')
bm.start()

'''