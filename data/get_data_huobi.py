# -*- coding: utf-8 -*-

from websocket import create_connection
import gzip
import time
from pymongo import MongoClient

def get_rt_data():

    client = MongoClient('localhost', 27017)
    coin_db = client['coindb']
    collection = coin_db['coin_market']

    while (1):
        try:
            ws = create_connection("wss://api.huobipro.com/ws")
            break
        except:
            print('connect ws error,retry...')
            time.sleep(5)

    # 订阅 KLine 数据
    tradeStr = """{"sub": "market.btcusdt.kline.1min","id": "id10"}"""

    # 请求 KLine 数据
    # tradeStr="""{"req": "market.ethusdt.kline.1min","id": "id10", "from": 1513391453, "to": 1513392453}"""

    # 订阅 Market Depth 数据
    # tradeStr="""{"sub": "market.ethusdt.depth.step5", "id": "id10"}"""

    # 请求 Market Depth 数据
    # tradeStr="""{"req": "market.ethusdt.depth.step5", "id": "id10"}"""

    # 订阅 Trade Detail 数据
    # tradeStr="""{"sub": "market.ethusdt.trade.detail", "id": "id10"}"""

    # 请求 Trade Detail 数据
    # tradeStr="""{"req": "market.ethusdt.trade.detail", "id": "id10"}"""

    # 请求 Market Detail 数据
    # tradeStr="""{"req": "market.ethusdt.detail", "id": "id12"}"""

    ws.send(tradeStr)

    while (1):
        compressData = ws.recv()
        result = gzip.decompress(compressData).decode('utf-8')
        if result[:7] == '{"ping"':
            ts = result[8:21]
            pong = '{"pong":' + ts + '}'
            ws.send(pong)
            ws.send(tradeStr)
        else:
            print('当前请求结果')
            print(result)
            if (type(result)==str and "tick" in result):
                mkt_data =  eval(result)
                tick = mkt_data ['tick']
                tick['coin'] = 'btcusd'
                tick['ts'] = mkt_data['ts']
                tick['time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tick['id']))
                try:
                    print(tick)
                    collection.insert_one(tick)
                except:
                    print('Data insert into mongodb Error!')



def get_hist_data(code = 'btcusdt', begin='2017-12-16 10:30:00', end= '2017-12-16 10:40:00'):

    client = MongoClient('localhost', 27017)
    coin_db = client['coindb']
    collection = coin_db['coin_market']

    while (1):
        try:
            ws = create_connection("wss://api.huobipro.com/ws")
            break
        except:
            print('connect ws error,retry...')
            time.sleep(5)

    # 请求 KLine 数据
    begin_unix = int(time.mktime(time.strptime(begin, '%Y-%m-%d %H:%M:%S')))
    end_unix = int(time.mktime(time.strptime(end, '%Y-%m-%d %H:%M:%S')))
    # tradeStr="{'req': 'market." + code + ".kline.1min','id': 'id10', 'from': " + str(begin_unix) + ", 'to': " + str(end_unix) + "}"
    tradeStr = """{"req": "market.btcusdt.kline.1min","id": "id10", "from": 1513391400, "to": 1513392000}"""
    print(tradeStr)
    ws.send(tradeStr)

    compressData = ws.recv()
    result = gzip.decompress(compressData).decode('utf-8')
    print(result)
    if result[:7] == '{"ping"':
        ts = result[8:21]
        pong = '{"pong":' + ts + '}'
        ws.send(pong)
        ws.send(tradeStr)
    else:
        print('当前请求结果')
        print(result)
        if (type(result)==str and "data" in result):
            mkt_data = eval(result)
            mkt_data = mkt_data ['data']
            for each in mkt_data:
                tick = each
                tick['time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tick['id']))
                try:
                    print(tick)
                    collection.insert_one(tick)
                except:
                    print('Data insert into mongodb Error!')

if __name__ == '__main__':

    get_hist_data()