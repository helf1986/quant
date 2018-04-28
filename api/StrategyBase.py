# -*- coding: utf-8 -*-
"""
Created on Wed Apr 25 16:02:09 2018

@author: ShuangJi.He
"""
#from gmsdk import to_dict,md
#md.init('18512101480', 'Hsj123')
import os;os.chdir(r'C:\Users\Administrator\Desktop\helf\quantbtc')
import api.quant_api as qapi
from api import logger
import time
import os
from queue import Queue, Empty
import threading    
#-----交易的基类---------
class Strategy(object):
    def __init__(self,module='usdt',api=qapi,exchange='huobipro',symbol_list='btcusdt',bar_type='1min' ):
#    def __init__(self,module='usdt',api=md,exchange='SHSE',symbol_list='600000',bar_type=60 ):
        self.prt=True#是否启动基类中的打印
        '''
        交易模式module：
            1、usdt：现金计价，即绝对收益型
            2、btc：比特币计价，即指数增强型
        
        数据源db_source：
            掘金=md
            火币=qapi
        
        '''
        
        self.module=module
        self.api=api

        #
        self.MarketPosition=0           # 策略仓位记录
        self.id=None#策略真实id，融资融券平仓需要
        # 订阅数据标的类型，周期类型
        self.exchange=exchange
        self.symbol_list=symbol_list
        self.bar_type=bar_type     
        #
        self.backbarnum=20      # 追溯历史回测bar数
        '''
        __barcount#记录当前推送bar数
        __type=数据状态,用以区分历史数据还是实时数据。默认'history'，满足条件后赋值为'realtime'        
        '''
        self.__barcount=0#记录当前推送bar数
        self.__type='history'
        '''
        不同事件类型分别记录
        __barqueue=bar记录队列，对应处理函数on_bar
        __lastquebar记录最新推送入队的bar
        __orderqueue=order记录队列，对应处理函数on_order
        '''
        self.__barqueue=Queue()
        self.__lastquebar=None
        self.__orderqueue=Queue()
        
#-----------------eventprocess函数-----------------    
    '''
       交易类
    '''
    def buy(self,unit,price):
        '''
        分原来是否持仓，是则先平后进
        '''
        if self.MarketPosition==-1:
            self.MarketPosition=0;print ("pre_buytocover(%s,%s)"%(unit,price))            
            if self.__type=='realtime':
                if self.module=='usdt':order=self.api.marginsec_close(exchange='huobipro', source='margin-api', sec_id='btcusdt', price=0, volume=unit,margin_order_id=self.id)              
                if self.module=='btc': order=self.api.close_short(exchange='huobipro', source='margin-api', sec_id='btcusdt', price=0, volume=unit)
        if self.MarketPosition==0:
            self.MarketPosition=1;print ("buy(%s,%s)"%(unit,price) )     
            if self.__type=='realtime':
                if self.module=='usdt':order=self.api.open_long(exchange='huobipro', source='margin-api', sec_id='btcusdt', price=0, volume=unit)
                if self.module=='btc': order=self.api.margincash_open(exchange='huobipro', source='margin-api', sec_id='btcusdt', price=0, volume=unit)    
                self.__orderqueue.put(order)  
                self.id=order.margin_order_id  
            
    def sellshort(self,unit,price):
        if self.MarketPosition==1:   
            self.MarketPosition=0;print ("pre_sell(%s,%s)"%(unit,price) )           
            if self.__type=='realtime':
                if self.module=='usdt':order=self.api.close_long(exchange='huobipro', source='margin-api', sec_id='btcusdt', price=0, volume=unit)  
                if self.module=='btc':order=self.api.margincash_close(exchange='huobipro', source='margin-api', sec_id='btcusdt', price=0, volume=unit,margin_order_id=self.id)        
        if self.MarketPosition==0:
            self.MarketPosition=-1;print ("sellshort(%s,%s)"%(unit,price) )
            if self.__type=='realtime':
                if self.module=='usdt':order=self.api.marginsec_open(exchange='huobipro', source='margin-api', sec_id='btcusdt', price=0, volume=unit)   
                if self.module=='btc':order=self.api.open_short(exchange='huobipro', source='margin-api', sec_id='btcusdt', price=0, volume=unit)   
                self.__orderqueue.put(order)  
                self.id=order.margin_order_id            
    def sell(self,unit,price):
        if self.MarketPosition==1:
            self.MarketPosition=0;print ("sell(%s,%s)"%(unit,price))
            if self.__type=='realtime':
                if self.module=='usdt':order=self.api.close_long(exchange='huobipro', source='margin-api', sec_id='btcusdt', price=0, volume=unit)  
                if self.module=='btc': order=self.api.margincash_close(exchange='huobipro', source='margin-api', sec_id='btcusdt', price=0, volume=unit,margin_order_id=self.id)  
                self.__orderqueue.put(order)  
    def buytocover(self,unit,price):
        if self.MarketPosition==-1:
            self.MarketPosition=0;print ("buytocover(%s,%s)"%(unit,price))
            if self.__type=='realtime':
                if self.module=='usdt':order=self.api.marginsec_close(exchange='huobipro', source='margin-api', sec_id='btcusdt', price=0, volume=unit,margin_order_id=self.id)              
                if self.module=='btc':order=self.api.close_short(exchange='huobipro', source='margin-api', sec_id='btcusdt', price=0, volume=unit)              
                self.__orderqueue.put(order)  
    '''
    基准类
    '''
    def on_bar(self,bar):
        '''
        barcount必须更新以识别历史数据和实时数据
        '''
        self.__barcount+=1
        #-----------------------
        if self.prt:
            print ('~~~~~~~~~~~' )   
            print (u"执行中.....,strtime=%s,barcount=%s,type=%s,queuesize=%s"%(bar.strtime,self.__barcount,self.__type,self.__barqueue.qsize()) )
            print ('~~~~~~~~~~~' ) 
        pass
#-------------------- -----更新事件队列-------------------------------------------
    def __sendevent_bar(self):   
        
        """发送事件，向事件队列中存入事件"""
        bars=self.api.get_bars_local(self.exchange, self.symbol_list, self.bar_type, size=self.backbarnum)
#        bars=self.api.get_last_n_bars(self.exchange+'.'+self.symbol_list,self.bar_type,self.backbarnum)
#        bars.reverse()
        for bar in bars:
#            print u"history---bar存入队列:",bar.strtime
            self.__barqueue.put(bar);self.__lastquebar=bar        
        while True:         
            bar = (self.api.get_bars(self.exchange, self.symbol_list, self.bar_type, size=1))[0]
#            bar = (self.api.get_last_bars(self.exchange+'.'+self.symbol_list,self.bar_type))[0]            
            #barqueue为空值或时间戳有更新时，才更新队列
            try:               
                if bar.utc_time>self.__lastquebar.utc_time:
                    self.__barqueue.put(bar);self.__lastquebar=bar                        
                    if self.prt:
                        print ('~~~~~~~~~~~'   )
                        print (u"realtime---bar存入队列:",bar.strtime,self.__barqueue.qsize() ) 
                        print ('~~~~~~~~~~~'   )

            except:  
                pass   
            '''
            防止死循环
            '''
            time.sleep(0.5)            
    #---------------------------主引擎-------------------------------------------    
    #----------------------------------------------------------------------
    def Start(self):
        """启动"""
        #子线程1=bar线事件订阅管理
        tson=threading.Thread(target=self.__sendevent_bar)
        tson.setDaemon(True)#后台线程自动结束
        tson.start()
        """引擎运行"""
        while True:
            if self.__barcount==self.backbarnum:self.__type='realtime'
            # 优先处理bar类事件
            try:
                bar = self.__barqueue.get_nowait() 
                self.on_bar(bar)
            except:
                pass
#            try:
#                order=self.__orderqueue.get()  
#                self.on_order(order)
#            except:
#                pass  
    #----------------防止死循环-----------
            time.sleep(0.001)
#================================================================
if __name__ == '__main__':
    #os.chdir(r'C:\Users\Administrator\Desktop\helf\quantbtc')
    #import api.quant_api as qapi
    #from api import logger 
    test=Strategy()
    test.Start()