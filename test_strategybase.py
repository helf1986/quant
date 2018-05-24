from api.StrategyBase_ft import Strategy, Event,cerebro

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

    input_exchange = 'hbp'
    input_api_key = "a4594cdd-75b0037b-003d37ea-528bd"
    input_api_secret = "5f0ea6d5-a4ff1afc-9c04e15a-9e3ba"
    input_currency = 'usdt'
    input_account = 'helf'

    myacc = cerebro(exchange=input_exchange, api_key=input_api_key, api_secret=input_api_secret, currency=input_currency, account=input_account)
    myacc.eventbarlist = [input1, input2]
    myacc.initialtion()
    myacc.addstrategy(type_=input1.type_, strats=mystr1)
    myacc.Start()
