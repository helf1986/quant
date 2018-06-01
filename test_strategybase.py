from api.StrategyBase_ft import Strategy, Event,cerebro
from multiprocessing import Process, Queue
from api.quant_api import TradeAccount, to_dict, to_dataframe

import time

btc_tick = []
btc_bar = []
btc_depth = []

def on_tick(tick_data):
	'''
	在此定义策略操作
	'''
	if len(tick_data) > 0:
		last_tick = tick_data[-1]
		struct_time = time.localtime(last_tick.utc_time/1000)
		if struct_time.tm_sec == 0:	
			print("~~~~~~~~~~~~~~~~~~~~~~~~", last_tick.strtime, last_tick.last_price)
			
	
def process_ontick(queue):

	global btc_tick
	while True:
		last_tick = queue.get()
		# print("--------------------", to_dict(last_tick))
		btc_tick = btc_tick + [last_tick]
		on_tick(btc_tick)

		
if __name__ == '__main__':


    # 定义策略
    mystr1 = Strategy(name="StrategyBase1")
    mystr2 = Strategy(name="StrategyBase2")

    # 创建核心<>单账户接口
    #
    input1 = Event()
    input1.symbol_list = 'btcusdt'
    input1.bar_type = 'tick'
    input1.backbarnum = 10
    input1.type_ = input1.symbol_list + input1.bar_type

    input2 = Event()
    input2.symbol_list = 'btcusdt'
    input2.bar_type = 'depth'
    input2.backbarnum = 20
    input2.type_ = input2.symbol_list + input2.bar_type

    input3 = Event()
    input3.symbol_list = 'btcusdt'
    input3.bar_type = '1min'
    input3.backbarnum = 20
    input3.type_ = input3.symbol_list + input3.bar_type


    input_exchange = 'hbp'
    input_api_key = "a4594cdd-75b0037b-003d37ea-528bd"
    input_api_secret = "5f0ea6d5-a4ff1afc-9c04e15a-9e3ba"
    input_currency = 'usdt'
    input_account = 'helf'

    myacc = cerebro(exchange=input_exchange, api_key=input_api_key, api_secret=input_api_secret, currency=input_currency, account=input_account)
    myacc.eventbarlist = [input1, input2, input3]
    myacc.initialtion()
    myacc.addstrategy(type_=input1.type_, strats=mystr1)
    myacc.Start()

	
    '''
    
    TEST_ACCESS_KEY = "a4594cdd-75b0037b-003d37ea-528bd"
    TEST_SECRET_KEY = "5f0ea6d5-a4ff1afc-9c04e15a-9e3ba"
    
    myaccount = TradeAccount(exchange='hbp', api_key=TEST_ACCESS_KEY, api_secret=TEST_SECRET_KEY, currency='USDT')
    
    # queue = Queue()
    # myaccount.subscribe_bar(symbol='btcusdt', bar_type='tick', queue=queue)


    queue_btctick = Queue()
    process1 = Process(target=myaccount.subscribe_bar, args=('btcusdt', 'tick', 1, queue_btctick))
    process1.start()
    print('Process 1 has started')

    
    queue_ethtick = Queue()
    process2 = Process(target=myaccount.subscribe_bar, args=('ethusdt', 'tick', 2, queue_ethtick))
    process2.start()
    
    print('Process 2 has started')
    
    process3 = Process(target=process_ontick, args=(queue_btctick, ))
    process3.start()
    print('Process 3 has started')
    '''