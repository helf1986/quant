#!/usr/bin/python3

import threading
import time
from websocket import create_connection
import gzip

exitFlag = 0

class myThread (threading.Thread):

    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        print ("开始线程：" + self.name)
        print_time(self.name, self.counter, 5)
        print ("退出线程：" + self.name)


class Subscribe_Bars (threading.Thread):

    def __init__(self, exchange, symbol, type):
        threading.Thread.__init__(self)
        self.exchange = exchange        # 交易所：hbp, bnb
        self.symbol = symbol            # 数币符号：ethbtc, ltcbtc, etcbtc, bchbtc......
        self.type = type                # bar 类型：1min, 5min, 15min, 30min, 60min, 1day, 1mon, 1week, 1year

    def run(self):

        while (1):
            try:
                ws = create_connection("wss://api.huobipro.com/ws")
                break
            except:
                print('connect ws error,retry...')
                time.sleep(5)

        # 订阅 KLine 数据
        tradeStr = """{"sub": "market.ethusdt.kline.1min","id": "id10"}"""

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
                print(result)


def print_time(threadName, delay, counter):
    while counter:
        if exitFlag:
            threadName.exit()
        time.sleep(delay)
        print ("%s: %s" % (threadName, time.ctime(time.time())))
        counter -= 1

# 创建新线程
thread1 = Subscribe_Bars(exchange='hbp', symbol='btcusdt', type='1min')
thread2 = myThread(2, "Thread-2", 2)

# 开启新线程
thread1.start()
# thread1.join()

# thread2.start()
# thread2.join()
# print ("退出主线程")