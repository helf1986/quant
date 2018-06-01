# -*- coding: utf-8 -*-
"""
Created on Tue May 29 21:59:05 2018

@author: helf
"""


import urllib.request
import re
import pandas as pd


coin = 'litecoin'
start_date = '20160101'
end_date = '20180529'

url = "https://coinmarketcap.com/zh/currencies/" + coin + "/historical-data/?start=" + start_date + "&end=" + end_date

response = urllib.request.urlopen(url)
data = response.read()

data = data.decode("utf-8")

pattern = re.compile(r'<tr class="text-right">.*?</tr>', re.S)
item_list = pattern.findall(data)

data_dict = {}
columns = ['open', 'high', 'low', 'close', 'volume', 'marketcap']
for each in item_list:
    reg = re.compile("\d\d\d\d年\d\d月\d\d日", re.S)
    tmp = reg.findall(each)
    if len(tmp) > 0:
        date = tmp[0]
    
    data_dict[date] = {}
    
    reg2 = re.compile(r'value=".*?</td>', re.S)
    tmp2 = reg2.findall(each)
    
    reg3 = re.compile(r'>.*?<', re.S)
    for nn in range(len(tmp2)):
        tmp3 = reg3.findall(tmp2[nn])
        if len(tmp3[0]) > 4:
            data_dict[date][columns[nn]] = float(tmp3[0][1:-1].replace(',', ''))

data_df = pd.DataFrame.from_dict(data_dict)
data_df = data_df.T

data_df.to_csv(coin+"_"+start_date+"_"+end_date+".csv")