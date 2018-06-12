
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

myfont = mpl.font_manager.FontProperties(fname='C:/Windows/Fonts/msyh.ttf')
mpl.rcParams['axes.unicode_minus'] = False

netvalue = pd.read_csv('docs/bitquant_result.csv', index_col=0, header=0, encoding='gbk')
netvalue.index = [each.split(' ')[0] for each in netvalue.index]
netvalue['Datetime'] = netvalue.index
netvalue.drop_duplicates(subset=['Datetime'], keep='last', inplace=True)
print(netvalue.tail())

fig = plt.figure()

ax1 = fig.add_subplot(111)
netvalue[['总资产(USDT)']].plot(kind='bar', ax=ax1, legend=True)
plt.legend(prop=myfont, loc='upper left')
ax1.set_ylim([80000, 160000])
ax1.set_ylabel('USDT', fontproperties=myfont)
# ax2.set_xlabel('日期', fontproperties=myfont)
ax1.set_title('BitQuant 净值报告', fontproperties=myfont)
plt.xticks(rotation=90)
# plt.gcf().autofmt_xdate()

ax2 = ax1.twinx()  # this is the important function
netvalue[['策略净值', '基准净值']].plot(ax=ax2, legend=True, grid=True)
plt.legend(prop=myfont, loc='upper right')
ax2.set_ylim([0.7, 1.1])
ax2.set_ylabel('净值', fontproperties=myfont)
ax2.set_xlabel('日期', fontproperties=myfont)
plt.xticks(rotation=90)
# plt.gcf().autofmt_xdate()

fig.tight_layout()
plt.show()
# plt.savefig('docs/quant_netvalue.png')

