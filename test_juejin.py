# -*- coding: utf-8 -*-

from api.quant_api import StrategyBase

class Mystrategy(StrategyBase):
    def __init__(self, *args, **kwargs):
        super(Mystrategy, self).__init__(*args, **kwargs)



if __name__ == '__main__':
    myStrategy = Mystrategy(
        username='-',
        password='-',
        strategy_id='',
        subscribe_symbols='',
        mode=2,
        td_addr='127.0.0.1:8001'
    )
    ret = myStrategy.run()
    print('exit code: ', ret)