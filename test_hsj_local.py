import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import api.quant_api as qapi
from api import logger

Vars = []
correct = 4
c1 = 1.751              # std 系数
l1 = 5                  # avg追溯时期
length = 100            # 基准期
length2 = 1             # 基准期

close = np.array([0]*length)
hp = np.array([0]*length)
lp = np.array([0]*length)
tot = np.array([0]*length)
net = np.array([0]*length)
nt = np.array([0]*length)


hp2 = np.array([0]*length)
lp2 = np.array([0]*length)
tot2 = np.array([0]*length)
net2 = np.array([0]*length)
nt2 = np.array([0]*length)
incon1 = False
incon2 = False
outcon = False

move = np.array([0]*length)
avg = np.array([0]*length)
std = np.array([0]*length)
move2 = np.array([0]*length)
avg2 = np.array([0]*length)
std2 = np.array([0]*length)
money = 0
unit = np.array([0]*length)
volstd = 0
i = 0
b1 = 0
b0 = 0
var1 = 0
var0 = 0

position = np.array([0]*length)
limit = np.array([0]*length)
most = 2

outcon1 = False
MarketPosition = 0

# length = length * correct

money = 200000
unit = 0

netvalue = pd.Series([1]*length)

btc_data = pd.read_csv('btc_data_201800405.csv')
print(btc_data.head())

data_df = btc_data[['ts', 'op', 'lp', 'hp', 'cp']].copy()
data_df.columns = ['time', 'open', 'low', 'high', 'close']
data_df.index = data_df['time']

for nn in range(length*l1, len(data_df)) :

    if nn >= length*l1:
        print(nn)
        mk_data = data_df[nn-length*l1:nn]
        mk_data = mk_data.sort_values(by='time')
        hp_now = np.max(mk_data['close'].iloc[-length:])
        hp = np.append(hp, [hp_now])

        lp_now = np.min(mk_data['close'].iloc[-length:])
        lp = np.append(lp, [lp_now])

        # 最近L天的涨跌幅绝对值之和 
        tot_now = np.sum(np.abs(np.log(mk_data['close'])-np.log(mk_data['close'].shift(1))).iloc[-length:].dropna())
        tot = np.append(tot, [tot_now])

        # 最高价最低价的振幅百分比
        net_now = np.log(hp[-1]) - np.log(lp[-1])   
        net = np.append(net, [net_now])

        # 理解为最近的振幅与过去L天振幅的比例
        nt_now = net[-1] / tot[-1] * 100
        nt = np.append(nt, [nt_now])

        # 过去L天的涨跌幅
        move_now = (mk_data['close'].iloc[-1]/mk_data['close'].iloc[-length] - 1)*100
        move = np.append(move, [move_now])

        avg_now = np.mean(nt[-length * l1:])
        avg = np.append(avg, [avg_now])

        std_now = np.std(nt[-length * l1:])
        std = np.append(std, [std_now])

        close_now = mk_data['close'].iloc[-1]
        close = np.append(close, [close_now])

        # 做多信号
        incon1 = (mk_data['close'].iloc[-1] >= hp[-1]) or ( (hp[-1] - mk_data['close'].iloc[-1]) / (mk_data['close'].iloc[-1] - lp[-1]) <= 0.2 and (hp[1] - mk_data['close'].iloc[-1]) / (mk_data['close'].iloc[-1] - lp[1]) >= 0 )
        
        # 做空信号
        incon2 = (mk_data['close'].iloc[-1] <= lp[-1]) or ( (hp[-1] - mk_data['close'].iloc[-1]) / (mk_data['close'].iloc[-1] - lp[-1]) >= 1 / 0.2 and (hp[-1] - mk_data['close'].iloc[-1]) / (mk_data['close'].iloc[-1] - lp[-1]) >= 0 )

        if (incon1):
            position_now = 1
        elif (incon2):
            position_now = -1
        else:
            position_now = 0
            
        print("position=" + str(position_now))
        
        position = np.append(position, [position_now])

        # 增加额外条件
        incon1 = (position_now == 1) and (nt[-1] >= avg[-1] + c1 * std[-1]) and (limit[-1] <= most) and (MarketPosition != 1)
        
        incon2 = (position_now == -1) and (nt[-1] >= avg[-1] + c1 * std[-1]) and (limit[-1] <= most) and (MarketPosition != -1)
        
        outcon = (nt[-1] < avg[-1])
        
        outcon1 = (nt[-1] >= avg[-1] + c1 * std[-1]) and (limit[-1] >= most + 1) and (MarketPosition != 0)


        if (incon1):    # 开多仓
            print('开多仓 @ %f' % mk_data['close'].iloc[-1])
            limit[-1] = limit[-1] + 1

        if (incon2):    # 平多仓
            print('开空仓 @ %f' % mk_data['close'].iloc[-1])
            limit[-1] = limit[-1] + 1

        if (outcon):    # 开空仓
            print('平多仓 @ %f' % mk_data['close'].iloc[-1])
            limit[-1] = 0

        if (outcon1):   # 平空仓
            print('平空仓 @ %f' % mk_data['close'].iloc[-1])


result = pd.DataFrame([], columns=['hp', 'lp', 'nt', 'move', 'avg', 'std'])
result['hp'] = hp
result['lp'] = lp
result['tot'] = tot
result['net'] = net
result['nt'] = nt
result['nt_avg'] = avg
result['nt_range'] = np.array(avg) + c1*np.array(std)
result['move'] = move
result['close'] = close

plt.figure(1)
result[['hp', 'lp', 'close']].iloc[length:].plot()

plt.figure(2)
result[['nt', 'nt_avg', 'nt_range']].plot()

plt.figure(3)
result[['move']].plot()