#!/usr/bin/python3

import threading
import time
from websocket import create_connection
import gzip
from queue import Queue

exitFlag = 0
from api.quant_api import Bar

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

QUEUE_SIZE = 2000
bar_queue = Queue(maxsize=QUEUE_SIZE)
last_bar = Bar()
bar_list = []

class Subscribe_Bars(threading.Thread):

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
            elif result[2:4] == "ch":
                # print(result)
                new_bar = Bar()
                data = result['tick']
                new_bar.utc_time = data['ts']
                structtime = time.localtime(data['ts'])
                new_bar.strtime = time.strftime('%Y-%m-%d %H:%M:%S', structtime)
                new_bar.open = data['open']
                new_bar.high = data['high']
                new_bar.low = data['low']
                new_bar.close = data['close']
                new_bar.volume = data['amount']
                new_bar.amount = data['volume']

                # 每分钟保留一个数据

                if last_bar.utc_time != new_bar.utc_time:
                    bar_queue.put(new_bar)


class Strategy(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):

        while(1):
            if bar_queue.qsize() > 0:
                new_bar = bar_queue.get()
                bar_list = bar_list + [new_bar]
                bar_list = bar_list[-QUEUE_SIZE:]
                print(len(bar_list))
                print(new_bar.strtime, new_bar.close)





def print_time(threadName, delay, counter):
    while counter:
        if exitFlag:
            threadName.exit()
        time.sleep(delay)
        print ("%s: %s" % (threadName, time.ctime(time.time())))
        counter -= 1

# 创建新线程
thread1 = Subscribe_Bars(exchange='hbp', symbol='btcusdt', type='1min')
thread2 = Strategy()

# 开启新线程
thread1.start()
thread2.start()

# thread1.join()

# thread2.start()
# thread2.join()
# print ("退出主线程")