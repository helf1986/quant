# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 17:22:21 2018

@author: ShuangJi.He
"""
from __future__ import division
#from gmsdk import to_dict,md
#md.init('18512101480', 'Hsj123')

import os
#from api.quant_api import TradeAccount, get_bars_local
from api.quant_api import to_dict,to_dataframe
#HBP_ACCESS_KEY = "a4594cdd-75b0037b-003d37ea-528bd"
#HBP_SECRET_KEY = "5f0ea6d5-a4ff1afc-9c04e15a-9e3ba"
#hbaccount = TradeAccount(exchange='hbp', api_key=HBP_ACCESS_KEY, api_secret=HBP_SECRET_KEY, currency='USDT')

from api import logger
import numpy as np
import math
#os.chdir(r'C:\Users\Administrator\Desktop\helf\quantbtc')
#import api.quant_api as qapi
#from api import logger
from api.StrategyBase_ft import Strategy,cerebro,Event
#~~~~~~~~~~~~~~~~~~~~~~

#-------------策略参数---------------------

#交易仓位参数
unit=0.001
jump=0.05/100
#-----------系统保留变量----------
systime=[]
maxbackbar=10#回测bar数=maxbackbar


class mystr(Strategy):
    def __init__(self,name='base_test'):
        super(mystr, self).__init__(name='base_test')
        #=============系统变量重置=====================
        self.prt=True#是否启动基类中的打印
    #---------数据缓存,需要管理的series变量----------    
        self.close_=[]
        self.hp_,self.lp_=[],[]
        self.net_,self.tot_,self.nt_=[],[],[]
    #---------策略变量----------   
        self.last=0
    def on_order(self,order):   
        super(mystr, self).on_order(order)
        print ("order output；\n",to_dict(order))
        pass
    def on_monitor(self,monitor):   
        super(mystr, self).on_monitor(monitor)
        print ("monitor output；\n",monitor)
        pass
    def on_bar(self,bar):      
        super(mystr, self).on_bar(bar)
        systime.append(bar.strtime)
        #====================================
        #-------策略参数计算------------------
#        if (self._Strategy__type!='history') and (self.last=='history' ):self.MarketPosition=-1
#        incon1=(self._Strategy__type!='history') and (self.MarketPosition!=1)
        incon1=False
        incon2=False
#        incon2=(self._Strategy__type!='history') and (self.MarketPosition==0)
#        outcon=(bar.strtime>='2018-05-06 21:14:00') and (bar.strtime<='2018-05-06 21:21:00')
        outcon=False    
        self.last=self._Strategy__type


        if (incon1):
            self.buy(unit,bar.close*(1+jump))
            print ("*(buy@...%s)"%(bar.strtime))

            
        if (incon2):
            self.sellshort(unit,bar.close*(1-jump))
            print ("(sellshort@...%s)"%(bar.strtime))

            
        if (outcon):
            if self.MarketPosition ==1:
                self.sell(unit,bar.close*(1-jump))
                print ("(sell@...%s)"%(bar.strtime))

                
            if self.MarketPosition ==-1:
                self.buytocover(unit,bar.close*(1+jump))
                print ("(buytocover@...%s)"%(bar.strtime))
        print (bar.strtime ,incon1,incon2,self.MarketPosition)

#======================需要管理的series变量=========================
        if len(systime)<maxbackbar:
            return
        elif len(systime)==maxbackbar:  
            self.MarketPosition=0
            print ("~~~~~~~~~~~~~~~~\n ")  
            print ("Success for preparing maxbackbar.... ")  
            print ("~~~~~~~~~~~~~~~~\n " ) 
        else :
            while (len(systime)>maxbackbar+1)  and (self._Strategy__type!='history'):
                systime.pop(0)        
                self.close_.pop(0)
                self.hp_.pop(0);self.lp_.pop(0);
                self.tot_.pop(0);self.net_.pop(0);self.nt_.pop(0) 
        #------------------------------                     

if __name__ == '__main__':

#    import sys;sys.path.append(r"C:\Users\Administrator\Desktop\helf\hesj09_strategy")
#    from HPTP import mystr as str_hptp
#    test=str_hptp()
    test1=mystr()
    
#------------------      
    input2=Event();
    input2.symbol_list= 'ethusdt';input2.bar_type= '1min';input2.backbarnum= 20;
    input2.type_=input2.symbol_list+input2.bar_type
    #
    input_account='helf'
    input_exchange='hbp'
    input_api_key= "a4594cdd-75b0037b-003d37ea-528bd"
    input_api_secret = "5f0ea6d5-a4ff1afc-9c04e15a-9e3ba"
    input_currency='usdt'
    #
    
    myacc=cerebro(exchange=input_exchange, api_key=input_api_key, api_secret=input_api_secret , currency=input_currency,
                 account=input_account)  
    myacc.eventbarlist=[input2]
    myacc.initialtion()
    myacc.addstrategy(type_=input2.type_, strats=test1)
    myacc.Start()   

