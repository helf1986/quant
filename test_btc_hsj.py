import numpy as np
import pandas as pd
import api.quant_api as qapi
from api import logger

Vars = []
correct = 4
c1 = 1.751      # std 系数
l1 = 5          # avg追溯时期
length = 100    # 基准期
length2 = 1        # 基准期

hp = [0]*length
lp = [0]*length
tot = [0]*length
net = [0]*length
nt = [0]*length

hp2 = [0]*length
lp2 = [0]*length
tot2 = [0]*length
net2 = [0]*length
nt2 = [0]*length
incon1 = False
incon2 = False
outcon = False

move = [0]*length
avg = [0]*length
std = [0]*length
move2 = [0]*length
avg2 = [0]*length
std2 = [0]*length
money = 0
unit = [0]*length
volstd = 0
i = 0
b1 = 0
b0 = 0
var1 = 0
var0 = 0
position = [0]*length
limit = [0]*length
most = 2
outcon1 = False


length = length * correct

money = 200000
unit = 0

while(1):
    bars = qapi.get_bars(exchange='huobipro', symbol_list='btcusdt', bar_type='1min', size=length + 100)
    if len(bars) > 0:
        mk_data = qapi.to_dataframe(bars)
        mk_data = mk_data[mk_data['sec_id'] == ' btcusdt']
        mk_data = mk_data.sort_values(by='time')
        hp = hp[1:] + [np.max(mk_data['close'].iloc[-length:])]
        lp = lp[1:] + [np.min(mk_data['close'].iloc[-length:])]
        tot = tot[1:] + tot [np.sum(np.abs(np.log(mk_data['close'].diff(1).iloc[-length:])))]
        net = net[1:] + [np.log(hp) - np.log(lp)]
        nt = nt[1:] + [net / tot * 100]
        move = move[1:] + [(mk_data['close'].iloc[-1]/mk_data['close'].iloc[-length] - 1)*100]
        avg = avg[1:] + [np.mean(nt.iloc[-length * l1:])]
        std = std[1:] + [np.std(nt.iloc[-length * l1:])]

        incon1 = (mk_data['close'].iloc[-1] >= hp[-1]) or ( (hp[-1] - mk_data['close'].iloc[-1]) / (mk_data['close'].iloc[-1] - lp[-1]) <= 0.2 and (hp[1] - mk_data['close'].iloc[-1]) / (mk_data['close'].iloc[-1] - lp[1]) >= 0 )
        incon2 = (mk_data['close'].iloc[-1] <= lp[-1]) or ( (hp[-1] - mk_data['close'].iloc[-1]) / (mk_data['close'].iloc[-1] - lp[-1]) >= 1 / 0.2 and (hp[-1] - mk_data['close'].iloc[-1]) / (mk_data['close'].iloc[-1] - lp[-1]) >= 0 )

        if (incon1):
            position = 1
        elif (incon2):
            position = -1
        else:
            position = 0
        print("position=" + str(position))

        incon1 = (position == 1) and (nt[1] >= avg + c1 * std) and (limit <= most) and (MarketPosition != 1)
        incon2 = (position == -1) and (nt[1] >= avg + c1 * std) and (limit <= most) and (MarketPosition != -1)
        outcon = (nt[1] < avg)
        outcon1 = (nt[1] >= avg + c1 * std) and (limit >= most + 1) and (MarketPosition != 0)


        if (incon1):
            qapi.open_long(exchange='huobipro', source='margin-api', sec_id='btcusdt', price=0, volume=unit)
            limit = limit + 1

        if (incon2):
            qapi.marginsec_open(exchange='huobipro', sec_id='btcusdt', price=0, volume=unit)
            limit = limit + 1

        if (outcon):
            qapi.close_long(exchange='huobipro', source='margin-api', sec_id='btcusdt', price=0, volume=unit)
            BuyToCover(unit, open)
            limit = 0

        if (outcon1):
            sell(unit, open);
            BuyToCover(unit, open)
