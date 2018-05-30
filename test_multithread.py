#!/usr/bin/python3

from threading import Thread
import time
from websocket import create_connection
import gzip
from queue import Queue

exitFlag = 0
from api.quant_api import Bar


class Subscribe_Bars(Thread):

    def __init__(self, ex, symbol, bar_type):
        Thread.__init__(self)
        self.exchange = ex              # 交易所：hbp, bnb
        self.symbol = symbol            # 数币符号：ethbtc, ltcbtc, etcbtc, bchbtc......
        self.bar_type = bar_type        # bar 类型：1min, 5min, 15min, 30min, 60min, 1day, 1mon, 1week, 1year

        self.QUEUE_SIZE = 5000          # 队列最大长度
        self.tick_queue = Queue(maxsize=self.QUEUE_SIZE)        # 存储历史tiks
        self.bar_queue = Queue(maxsize=self.QUEUE_SIZE)         # 存储历史bars

        self.tick_list = []     # 存储历史tiks
        self.bar_list = []      # 存储历史bars

        self.new_tick = Tick()
        self.new_bar = Bar()    # 记录最新的bar
        self.last_bar = Bar()   # 记录上一个bar

    def run(self):

        # 创建 websocket 连接
        while (1):
            try:
                ws = create_connection("wss://api.huobipro.com/ws")
                break
            except:
                print('connect ws error,retry...')
                time.sleep(5)

        # 订阅 KLine 数据
        tradeStr = """{"sub": "market.""" + self.symbol + """.kline.""" + self.bar_type + """"","id": "id10"}"""

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

                new_bar = Bar()
                new_bar.utc_endtime = result['']
                data = eval(result)['tick']
                new_bar.utc_time = data['id']
                structtime = time.localtime(data['id'])
                new_bar.strtime = time.strftime('%Y-%m-%d %H:%M:%S', structtime)
                new_bar.open = data['open']
                new_bar.high = data['high']
                new_bar.low = data['low']
                new_bar.close = data['close']
                new_bar.volume = data['amount']
                new_bar.amount = data['vol']

                self.new_bar = new_bar

                # 存入tick_list 中
                if self.bar_queue.qsize() == self.QUEUE_SIZE:
                    self.bar_queue.get()
                else:
                    self.bar_queue.put(new_bar)
                    print("websocket new_tick: %s : close = %.2f" %(new_bar.strtime, new_bar.close))
                    self.tick_list = self.tick_list + [new_bar]
                    self.tick_list = self.tick_list[-self.QUEUE_SIZE:]

            if self.last_bar.utc_time.tm_min != new_bar.utc_time:
                print("websockt last_bar: %s  %f" % (new_bar.strtime, new_bar.close))

                bar_list = bar_list + [new_bar]
                bar_list = bar_list[-self.QUEUE_SIZE:]
                self.last_bar = self.new_bar()


class Strategy(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.subscribe = Subscribe_Bars(ex='hbp', symbol='btcusdt', bar_type='1min')
        self.bar_list = []
        self.QUEUE_SIZE = 5000

    def run(self):
        '''
        此处定义策略
        :return:
        '''
        while(1):
            if self.subscribe.bar_queue.qsize() > 0:

                last_bar = self.subscribe.last_bar

                # 每分钟保留一个数据
                print("strategy: %s time=%s close= %.4f" %(last_bar.sec_id, last_bar.strtime, last_bar.close))



# 创建新线程
thread1 = Subscribe_Bars(ex='hbp', symbol='btcusdt', bar_type='1min')
thread1 = Subscribe_Bars(ex='hbp', symbol='ethusdt', bar_type='5min')

thread2 = Strategy()

# 开启新线程
thread1.start()
thread2.start()

# thread1.join()

# thread2.start()
# thread2.join()
# print ("退出主线程")