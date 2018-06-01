# -*- coding: utf-8 -*-
"""
Created on Wed May 30 10:51:49 2018

@author: Administrator
"""

import time
from websocket import create_connection
import gzip

symbol = 'ethusdt'
bar_type = '1min'

# 创建 websocket 连接

try:
    ws = create_connection("wss://api.huobipro.com/ws")

except:
    print('connect ws error,retry...')
    time.sleep(5)

# 订阅 KLine 数据
tradeStr = """{\"sub\": \"market.""" + symbol + """.kline.""" + bar_type + """\",\"id\": \"id10\"}"""
# tradeStr = """{"sub": "market.ethusdt.kline.1min","id": "id10"}"""

print(tradeStr)

ws.send(tradeStr)
while (1):
    compressData = ws.recv()
    result = gzip.decompress(compressData).decode('utf-8')
    print(result)
    if result[:7] == '{"ping"':
        ts = result[8:21]
        pong = '{"pong":' + ts + '}'
        ws.send(pong)
        ws.send(tradeStr)
    elif result[2:4] == "ch":
        
        print(result)
        