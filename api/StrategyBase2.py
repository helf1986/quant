# -*- coding: utf-8 -*-
"""
Created on Wed Apr 25 16:02:09 2018

@author: ShuangJi.He
"""

import os
import api.quant_api as qapi
from api import logger
import time
from queue import Queue
import threading
import json

# -------------------------------
# phone_list = "13811892804, 18512101480, 13910993289, 15818535870, 13911217190"
phone_list = "13811892804"


# -----交易的基类---------
class Strategy(object):
    def __init__(self, name="straname", module=['usdt', 'btc'], api=qapi, exchange='hbp', symbol_list='btcusdt',
                 bar_type='1min'):

        self.prt = True  # 是否启动基类中的打印

        '''
        交易模式module：module[0]用于标记模式，module[1]用于指示融券种类
            1、['usdt','btc']：现金计价，即绝对收益型
            2、['btc','usdt']：比特币计价，即指数增强型          
        接口源api：
            掘金=md
            火币=qapi       
        '''
        self.name = name
        self.module = module[0]
        self.margin_currency = module[1]
        self.api = api

        '''
        实时监控文件名
        监控数据格式
        '''
        self.filename = self.name + '_' + self.module + "2" + self.margin_currency + '.json'
        self.monitordata = {"margin_order_id": None}
        #
        self.MarketPosition = 0  # 策略仓位记录
        self.margin_order_id = None  # 策略融资融券id，融资融券平仓需要
        # 订阅数据标的类型，周期类型
        self.exchange = exchange
        self.symbol_list = symbol_list
        self.bar_type = bar_type
        #
        self.backbarnum = 20  # 追溯历史回测bar数

        '''
        __barcount#记录当前推送bar数
        __type=数据状态,用以区分历史数据还是实时数据。默认'history'，满足条件后赋值为'realtime'        
        '''
        self.__barcount = 0  # 记录当前推送bar数
        self.__type = 'history'

        '''
        不同事件类型分别记录
        __barqueue=bar记录队列，对应处理函数on_bar
        __lastquebar记录最新推送入队的bar
        __orderqueue=order记录队列，对应处理函数on_order
        '''
        self.__barqueue = Queue()
        self.__lastquebar = None
        self.__orderqueue = Queue()

        # 记录交易和持仓历史
        self.positions = []         # 记录本策略当前持仓明细
        self.position_records = []  # 记录历史持仓记录，每发生一次交易，历史持仓和净值变更一次。每日24:00:00，历史持仓和净值更新一次
        self.order_records = []     # 记录历史交易记录
        self.margin_records = []    # 记录历史融资融券订单


    # -----------------eventprocess函数-----------------
    '''
       交易类
    '''

    def buy(self, unit, price):
        '''
        分原来是否持仓，是则先平后进
        '''
        if self.MarketPosition == -1:
            self.MarketPosition = 0
            print(self.name + "pre_buytocover(%s,%s)" % (unit, price))
            if self.__type == 'realtime':
                if self.module == 'usdt':
                    '''
                    还券分三步：
                    1、确认融券量=本币+利息
                    2、买入足够数量券【可以执行拆单函数】
                    3、执行还券流程
                    '''
                    unpaid_volume = self.api.get_margin_volume(self.margin_order_id, currency=self.margin_currency)
                    order = self.api.open_long(exchange=self.exchange, source='margin-api', sec_id=self.symbol_list,
                                               price=price, volume=unpaid_volume)
                    self.api.repay_margin(exchange=self.exchange, margin_order_id=self.margin_order_id,
                                          amount=unpaid_volume)
                else:
                    order = self.api.open_long(exchange=self.margin_order_id, source='api', sec_id=self.symbol_list,
                                               price=price, volume=unit)
                self.__orderqueue.put(order)
        if self.MarketPosition == 0:
            self.MarketPosition = 1;
            print(self.name + "buy(%s,%s)" % (unit, price), self.MarketPosition)
            if self.__type == 'realtime':
                if self.module == 'usdt':
                    order = self.api.open_long(exchange=self.exchange, source='api', sec_id=self.symbol_list,
                                               price=price, volume=unit)
                else:
                    margin = self.api.apply_margin(exchange=self.exchange, symbol=self.symbol_list,
                                                   currency=self.margin_currency, amount=unit)
                    order = self.api.open_long(exchange=self.exchange, source='margin-api', sec_id=self.symbol_list,
                                               price=price, volume=unit)
                    self.margin_order_id = margin.margin_order_id
                self.__orderqueue.put(order)
                msg = " 开多仓 " + self.symbol_list + "@ %s,%f" % (unit, price)
                logger.info(msg)
                logger.send_sms(msg, phone_list)

    def sellshort(self, unit, price):
        if self.MarketPosition == 1:
            self.MarketPosition = 0;
            print(self.name + "pre_sell(%s,%s)" % (unit, price))
            if self.__type == 'realtime':
                if self.module == 'usdt':
                    order = self.api.close_long(exchange=self.exchange, source='api', sec_id=self.symbol_list,
                                                price=price, volume=unit)
                else:
                    unpaid_volume = self.api.get_margin_volume(self.margin_order_id, currency=self.margin_currency)
                    order = self.api.close_long(exchange=self.exchange, source='margin-api', sec_id=self.symbol_list,
                                                price=price, volume=unpaid_volume)
                    self.api.repay_margin(exchange=self.exchange, margin_order_id=self.margin_order_id,
                                          amount=unpaid_volume)
                self.__orderqueue.put(order)
        if self.MarketPosition == 0:
            self.MarketPosition = -1;
            print(self.name + "sellshort(%s,%s)" % (unit, price), self.MarketPosition)
            if self.__type == 'realtime':
                if self.module == 'usdt':
                    margin = self.api.apply_margin(exchange=self.exchange, symbol=self.symbol_list,
                                                   currency=self.margin_currency, amount=unit)
                    order = self.api.close_long(exchange=self.exchange, source='margin-api', sec_id=self.symbol_list,
                                                price=price, volume=unit)
                    self.margin_order_id = margin.margin_order_id
                else:
                    order = self.api.close_long(self.exchange, source='api', sec_id=self.symbol_list, price=price,
                                                volume=unit)

                self.__orderqueue.put(order)
                msg = " 开空仓 " + self.symbol_list + "@ %s,%f" % (unit, price)
                logger.info(msg)
                logger.send_sms(msg, phone_list)

    def sell(self, unit, price):
        if self.MarketPosition == 1:
            self.MarketPosition = 0;
            print(self.name + "sell(%s,%s)" % (unit, price), self.MarketPosition)
            if self.__type == 'realtime':
                if self.module == 'usdt':
                    order = self.api.close_long(exchange=self.exchange, source='api', sec_id=self.symbol_list,
                                                price=price, volume=unit)
                else:
                    unpaid_volume = self.api.get_margin_volume(self.margin_order_id, currency=self.margin_currency)
                    order = self.api.close_long(exchange=self.exchange, source='margin-api', sec_id=self.symbol_list,
                                                price=price, volume=unpaid_volume)
                    self.api.repay_margin(exchange=self.exchange, margin_order_id=self.margin_order_id,
                                          amount=unpaid_volume)
                self.__orderqueue.put(order)
                msg = " 平多仓 " + self.symbol_list + "@ %s,%f" % (unit, price)
                logger.info(msg)
                logger.send_sms(msg, phone_list)

    def buytocover(self, unit, price):
        if self.MarketPosition == -1:
            self.MarketPosition = 0;
            print(self.name + "buytocover(%s,%s)" % (unit, price), self.MarketPosition)
            if self.__type == 'realtime':
                if self.module == 'usdt':
                    unpaid_volume = self.api.get_margin_volume(self.margin_order_id, currency=self.margin_currency)
                    order = self.api.open_long(exchange=self.exchange, source='margin-api', sec_id=self.symbol_list,
                                               price=price, volume=unpaid_volume)
                    self.api.repay_margin(exchange=self.exchange, margin_order_id=self.margin_order_id,
                                          amount=unpaid_volume)
                else:
                    order = self.api.close_long(self.exchange, source='api', sec_id=self.symbol_list, price=price,
                                                volume=unit)
                self.__orderqueue.put(order)
                msg = " 平空仓 " + self.symbol_list + "@ %s,%f" % (unit, price)
                logger.info(msg)
                logger.send_sms(msg, phone_list)

    '''
    基准类
    '''

    def on_bar(self, bar):
        pass

    def on_order(self, order):
        '''
        此处处理输出order到数据库，包括历史表和实时表
        '''
        order

    # -------------------- -----更新事件队列-------------------------------------------
    def __sendevent_bar(self):

        """发送事件，向事件队列中存入事件"""
        bars = self.api.get_bars_local(self.exchange, self.symbol_list, self.bar_type, size=self.backbarnum)
        #        bars=self.api.get_last_n_bars(self.exchange+'.'+self.symbol_list,self.bar_type,self.backbarnum)
        #        bars.reverse()
        for bar in bars:
            #            print u"history---bar存入队列:",bar.strtime
            self.__barqueue.put(bar);
            self.__lastquebar = bar
        while True:
            bar = (self.api.get_bars(self.exchange, self.symbol_list, self.bar_type, size=1))[0]
            #            bar = (self.api.get_last_bars(self.exchange+'.'+self.symbol_list,self.bar_type))[0]
            # barqueue为空值或时间戳有更新时，才更新队列
            try:
                if bar.utc_time > self.__lastquebar.utc_time:
                    self.__barqueue.put(bar);
                    self.__lastquebar = bar
                    if self.prt:
                        print('~~~~~~~~~~~')
                        print(u"realtime---bar存入队列:", bar.strtime, self.__barqueue.qsize())
                        print('~~~~~~~~~~~')

            except:
                pass
            '''
            防止死循环
            '''
            time.sleep(0.5)
            # ---------------------------主引擎-------------------------------------------

    # ----------------------------------------------------------------------
    def Start(self):
        """启动"""
        # 子线程1=bar线事件订阅管理
        tson = threading.Thread(target=self.__sendevent_bar)
        tson.setDaemon(True)  # 后台线程自动结束
        tson.start()
        """引擎运行"""
        while True:
            '''
            历史bar全部遍历，开始实时数据推送;
            1、数据标记改为'realtime',最后一步    
            2、数据库读取当前融资融券id，如果有的话
            3、输出策略启动信息手机
            '''
            if self.__barcount == self.backbarnum:
                '''
                以下内容仅在历史数据推送完后执行一次
                '''
                if self.__type == 'history':
                    # -------------step 2-----------------
                    file = 'monitor/' + self.filename
                    if not os.path.exists(file):
                        with open(file, 'w') as f:
                            json.dump(self.monitordata, f)
                    else:
                        with open(file, 'r') as f:
                            self.monitordata = json.load(f)
                            self.margin_order_id = self.monitordata['margin_order_id']
                    # --------------step 3--------------
                    msg = " Strategy(%r) on [%s,%s] is restarting @ %s..." % (
                    self.name, self.module, self.margin_currency, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                    logger.info(msg)
                    logger.send_sms(msg, phone_list)
                    # --------------step 1--------------
                    print(u"history data feeded successfully...realtime data on going")
                    self.__type = 'realtime'
            # 优先处理bar类事件
            try:
                bar = self.__barqueue.get_nowait()
                '''
                barcount必须更新以识别历史数据和实时数据
                '''
                self.__barcount += 1
                if self.prt:
                    print('~~~~~~~~~~~')
                    print(u"执行中.....,strtime=%s,barcount=%s,type=%s,queuesize=%s" % (
                    bar.strtime, self.__barcount, self.__type, self.__barqueue.qsize()))
                    print('~~~~~~~~~~~')
                pass
                # -----------------------
                self.on_bar(bar)
            except:
                pass
            # 开始处理order事件
            try:
                order = self.__orderqueue.get_nowait()
                self.on_order(order)
            except:
                pass
                # ----------------防止死循环-----------
            time.sleep(0.001)


# ================================================================
if __name__ == '__main__':
    # os.chdir(r'C:\Users\Administrator\Desktop\helf\quantbtc')
    # import api.quant_api as qapi
    # from api import logger
    test = Strategy()
    test.Start()