from __future__ import division
#from gmsdk import to_dict,md
#md.init('18512101480', 'Hsj123')
import os
from api.quant_api import TradeAccount, get_bars_local
from api.quant_api import to_dict
from api import logger
import time
# from queue import Queue
import threading

from multiprocessing import Process, Queue
import json
import math
import api.connection as conn
import pandas as pd

class Event():
    '''
    订阅事件对象，cerebro基础输入
    '''
    def __init__(self):
        self.symbol_list = ''                   # 币种
        self.bar_type = ''                       # 周期
        self.backbarnum = None                  # 历史数据数目
        self.type_ = ''                           # 自定义数据类别--用于注册监听函数字典


#-------------------------------------------------------------
class cerebro(object):

    def __init__(self,exchange='', api_key='', api_secret='' , currency='', account=''):
        '''
        执行cerebro需要初始化eventbarlist，及监听函数
        eventbarlist:bar 事件订阅列表,订阅x品种x周期的数据
        __handlers：对应的事件的响应函数，键值来自__eventbarlist
            * 每个键对应的值是一个列表，列表中保存了对该事件监听的响应函数，一对多
        '''

        self.account    = account
        self.api        = TradeAccount(exchange=exchange, api_key=api_key, api_secret=api_secret , currency=currency)
        self.prt            = False
        self.eventbarlist   = []
        self.__handlers     = {}
        self.__concount     = 0         # 断线重连计数

    def initialtion(self):
        '''
        不同事件类型分别记录
        __barqueue=bar记录队列，对应处理函数on_bar; __lastquebar记录最新推送入队的bar
        '''

        for v in self.eventbarlist:
            v.barqueue      = Queue()
            v.lastquebar    = None

        for v in self.eventbarlist:
            if v.bar_type == 'tick':        # 目前本地数据库不支持tick数据
                # print('tick data sent into queues')
                pass
            else:
                bars            = get_bars_local(exchange=self.api.exchange,symbol_list=v.symbol_list, bar_type=v.bar_type, size=v.backbarnum)
                v.backbarnum    = len(bars) # 修正取数据误差
                for bar in bars:
                    v.barqueue.put(bar)
                    v.lastquebar = bar


    #-------------------------更新事件队列-------------------------------------------
    def __sendevent_bar(self):
        '''
        发送事件，向事件队列中存入事件
        :return:
        '''

        client_num = 0
        for v in self.eventbarlist:
            v_process = Process(target=self.api.subscribe_bar, args=(v.symbol_list, v.bar_type, client_num, v.barqueue))
            v_process.start()
            print(v.symbol_list + " " + v.bar_type + " has been started!")
            client_num += 1

    #---------------------------主引擎-------------------------------------------
    def MainEngine(self):

        print('Main Engine has been started!')
        """引擎运行"""
        while True:

            # 优先处理bar类事件
            '''bar执行逻辑为一对多'''
            try:
                for v in self.eventbarlist:
                    bar = v.barqueue.get_nowait()
                    if self.prt:
                        print("%s 当前bar: %s, close=%.4f" % (bar.sec_id, bar.strtime, bar.close))

                    # 检查是否存在对该事件进行监听的处理函数
                    if v.type_ in self.__handlers:
                        # 若存在，则按顺序将事件传递给处理函数执行
                        for strats in self.__handlers[v.type_]:
                            strats.on_bar(bar)
            except:
                pass

            # 开始处理monitor事件,优先于order
            '''monitor执行逻辑为完全遍历'''
            try:
                for v in self.eventbarlist:
                    for strats in self.__handlers[v.type_]:
                        strats.monitorprocess()
            #                for strats in self.stratslist:
            #                    strats.monitorprocess()
            except:
                pass

            # 开始处理order事件
            '''order执行逻辑为完全遍历'''
            try:
                for v in self.eventbarlist:
                    for strats in self.__handlers[v.type_]:
                        strats.orderprocess()
                        #                for strats in self.stratslist:
            #                    strats.orderprocess()
            except:
                pass

            # ----------------防止死循环-----------
            time.sleep(0.01)

    # ---------------------------启动策略------------------------------------------
    def Start(self):
        """启动"""

        # 多进程进行事件订阅管理
        self.__sendevent_bar()

        # 新建一个进程，执行主引擎
        engine_process = Process(target=self.MainEngine)
        engine_process.start()

    def addstrategy(self,type_,strats):
        '''
        本函数只接受单独运行，一次添加一个策略
        '''
        try:
            '''
            单策略初始化：回调单策略的接口参数
            '''
            strats.api=self.api
            for v in self.eventbarlist:
                if v.type_==type_:
                    #
                    strats.backbarnum=v.backbarnum
                    strats.symbol_list=v.symbol_list
                    strats.bar_type=v.bar_type
                    #
                    strats.account=self.account
                    strats.module=str.lower(self.api.currency)
                    strats.margin_currency=strats.symbol_list.strip(strats.module)
                    #
                    strats.initialtion()
                    #
                    break

            """绑定事件和监听器处理函数"""
            # 尝试获取该事件类型对应的处理函数列表，若无则创建
            try:
                stratslist = self.__handlers[type_]
            except KeyError:
                stratslist = []
            self.__handlers[type_] = stratslist
            if strats not in self.__handlers[type_]:
                self.__handlers[type_].append(strats)
#            self.stratslist.append(strats)
        except:
            logger.warn ("adding strategy wrong!!!")
