
# 从api接口导入TradeAccount 交易类
from api.quant_api import TradeAccount, to_dataframe, to_dict, get_bars_local
import time
import pandas as pd
from api import logger
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

test_api_key = "a4594cdd-75b0037b-003d37ea-528bd"
test_secret_key = "5f0ea6d5-a4ff1afc-9c04e15a-9e3ba"

myacc = TradeAccount(exchange='hbp', api_key=test_api_key, api_secret=test_secret_key, currency='USDT')

total_filled_volume, total_filled_amount, order_list = myacc.order_split(source='api', sec_id='btcusdt', side=1, price=0, volume=0.004, max_ratio=0.1)
print(total_filled_volume, total_filled_amount)