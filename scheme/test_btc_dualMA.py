# -*- coding: utf-8 -*-
"""
Created on Wed Mar 14 20:40:23 2018

@author: helf
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

data = pd.read_excel('btcusd_gdax.xlsx', 'Sheet2', index_col=0, header=0)
print(data.head())

N_short = 5
N_long = 20
data['pct_chg'] = data['close'].pct_change()
data['ma_short'] = data['close'].rolling(N_short).mean()
data['ma_long'] = data['close'].rolling(N_long).mean()


'''
plt.figure(figsize=(6,12))
axe1 = plt.subplot(2,1,1)
data[['close', 'ma_short', 'ma_long']].plot()
axe2 = plt.subplot(2,1,2)
data['volume'].plot()
plt.tight_layout()
plt.show()
'''

data['signal'] = 0
data['account'] = 1

for nn in range(N_long+1, len(data)):
    
    # 向上突破，买入
    if (data['ma_short'].iloc[nn-2] < data['ma_long'].iloc[nn-2]) and  \
    (data['ma_short'].iloc[nn-1] > data['ma_long'].iloc[nn-1]):
        data['signal'].iloc[nn-1] = 1
    
    # 向下突破，卖出
    elif (data['ma_short'].iloc[nn-2] > data['ma_long'].iloc[nn-2]) and  \
    (data['ma_short'].iloc[nn-1] < data['ma_long'].iloc[nn-1]):
        data['signal'].iloc[nn-1] = -1
    
    else:
        data['signal'].iloc[nn-1] = data['signal'].iloc[nn-2]
    
    # 计算账户
    if data['signal'].iloc[nn-1] == -1: # 做空
        data['account'].iloc[nn] = data['account'].iloc[nn-1]

    elif data['signal'].iloc[nn-1] == 1: # 做多
        data['account'].iloc[nn] = data['account'].iloc[nn-1]*(1+data['pct_chg'].iloc[nn])


result = data.iloc[0:]
fig = plt.figure(figsize=(6,12))
ax1 = fig.add_subplot(211)
ax1.plot(result.index, result['close'])
ax1.set_ylabel('Close')
# plt.legend(['close'], loc='best')

ax2 = ax1.twinx()  # this is the important function
ax2.plot(result.index, result['signal'], 'r')
ax2.set_ylabel('Signal')
# plt.legend(['signal'], loc='best')

ax3 = fig.add_subplot(212)
ax3.plot(result.index, result['account'])
plt.legend(['account'], loc='best')

plt.show()


# 业绩评估
# 业绩评估
from fund_perform_eval import *

perform_res = PerformEval(net_value=data['account'], benchmark_value=data['close'], riskfree_rate=0, return_type='d')
perform_res = pd.DataFrame.from_dict(perform_res, orient='index')
print(perform_res)