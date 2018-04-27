import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import api.quant_api as qapi
from api import logger

# 定义参数
correct = 4
c1 = 1.75  # std 系数
l1 = 5  # avg追溯时期
length = 100  # 基准期
length2 = 1  # 基准期

btc_data = pd.read_csv('btc_data_20171101_20180325.csv')
print(btc_data.head())

df = btc_data[['ts', 'op', 'lp', 'hp', 'cp']].iloc[0:2000].copy()
df.columns = ['time', 'open', 'low', 'high', 'close']
df.index = df['time']

df['hp'] = df['close']
df['lp'] = df['close']
df['tot'] = 0
df['net'] = 0
df['nt'] = 0

df['hp2'] = 0
df['lp2'] = 0
df['tot2'] = 0
df['net2'] = 0
df['nt2'] = 0

incon1 = False
incon2 = False
outcon = False

df['move'] = 0
df['avg'] = 0
df['std'] = 0
df['move2'] = 0
df['avg2'] = 0
df['std2'] = 0
money = 0
df['unit'] = 0
volstd = 0
i = 0
b1 = 0
b0 = 0
var1 = 0
var0 = 0

most = 2
outcon1 = False
MarketPosition = 0

# length = length * correct

money = 200000
unit = 0

df['position'] = 0
df['Market_Position'] = 0
df['limit'] = 0
df['netvalue'] = 1

for nn in range(length * l1, len(df)):

    rt_data = df.iloc[nn - length * l1:nn].copy()
    rt_data = rt_data.sort_values(by='time')

    now = rt_data.index[-1]
    last = rt_data.index[-2]

    close_now = rt_data['close'].iloc[-1]
    close_last = rt_data['close'].iloc[-2]

    hp_now = np.max(rt_data['close'].iloc[-length:])
    df.loc[now, 'hp'] = hp_now

    lp_now = np.min(rt_data['close'].iloc[-length:])
    df.loc[now, 'lp'] = lp_now

    # 最近L天的涨跌幅绝对值之和
    tot_now = np.sum(np.abs(np.log(rt_data['close']) - np.log(rt_data['close'].shift(1))).iloc[-length:].dropna())
    df.loc[now, 'tot'] = tot_now

    # 最高价最低价的振幅百分比
    net_now = np.log(hp_now) - np.log(lp_now)
    df.loc[now, 'net'] = net_now

    # 理解为最近的振幅与过去L天振幅的比例
    nt_now = net_now / tot_now * 100
    df.loc[now, 'nt'] = nt_now

    # 过去L天的涨跌幅
    move_now = (rt_data['close'].iloc[-1] / rt_data['close'].iloc[-length] - 1) * 100
    df.loc[now, 'move'] = move_now

    avg_now = np.mean(df['nt'].iloc[nn - length * l1:nn])
    df.loc[now, 'avg'] = avg_now

    std_now = np.std(df['nt'].iloc[nn - length * l1:nn])
    df.loc[now, 'std'] = std_now

    close_now = rt_data['close'].iloc[-1]
    df.loc[now, 'close'] = close_now

    # 做多信号
    incon1 = (close_now >= hp_now) or (
    (hp_now - close_now) / (close_now - lp_now) <= 0.2 and (hp_now - close_now) / (close_now - lp_now) >= 0)

    # 做空信号
    incon2 = (close_now <= lp_now) or (
    (hp_now - close_now) / (close_now - lp_now) >= 1 / 0.2 and (hp_now - close_now) / (close_now - lp_now) >= 0)

    if (incon1):
        position_now = 1
    elif (incon2):
        position_now = -1
    else:
        position_now = 0
    df.loc[now, 'position'] = position_now

    # 增加额外条件
    Market_Position_last = df['Market_Position'].iloc[nn - 1]
    limit_last = df['limit'].iloc[nn - 1]

    # 开多仓信号
    incon1 = (position_now == 1) and (nt_now >= avg_now + c1 * std_now) and (limit_last <= most) and (
    Market_Position_last != 1)

    # 开空仓信号
    incon2 = (position_now == -1) and (nt_now >= avg_now + c1 * std_now) and (limit_last <= most) and (
    Market_Position_last != -1)

    # 平仓信号
    outcon = (nt_now < avg_now)

    outcon1 = (nt_now >= avg_now + c1 * std_now) and (limit_last >= most + 1) and (Market_Position_last != 0)

    Market_Position_now = Market_Position_last
    limit_now = limit_last

    if (incon1):  # 开多仓
        print('%s : 开多仓 @ %f' % (now, close_now))
        Market_Position_now = 1
        limit_now = limit_now + 1

    if (incon2):  # 开空仓
        print('%s : 开空仓 @ %f' % (now, close_now))
        Market_Position_now = -1
        limit_now = limit_now + 1

    if (outcon):  # 开空仓
        print('%s : 平多仓 @ %f' % (now, close_now))
        print('%s : 平空仓 @ %f' % (now, close_now))
        Market_Position_now = 0
        limit_now = 0

    if (outcon1):  # 平空仓
        print('%s : 平空仓 @ %f' % (now, close_now))
        Market_Position_now = 0
        limit_now = limit_now - 1

    df.loc[now, 'Market_Position'] = Market_Position_now
    df.loc[now, 'limit'] = limit_now
    # print("%s : market position = %s " % (now, str(Market_Position_now)))

df['nt_range'] = df['avg'] + c1 * df['std']

plt.figure(1)
df[['hp', 'lp', 'close']].iloc[length:].plot()

plt.figure(2)
df[['nt', 'avg', 'nt_range']].plot()

plt.figure(3)
df[['move']].plot()

plt.figure(4)
df['benchmark'] = df['close'] / df['close'].iloc[0]
df[['netvalue', 'benchmark']].plot()

df.to_csv('test_result.csv')