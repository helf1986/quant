
from common.settings import HBP_SECRET_KEY, HBP_ACCESS_KEY
from api.quant_api import TradeAccount, to_dataframe, to_dict, get_bars_local, Indicator, Tick, Order, Bar
import time
import pandas as pd
import numpy as np
import api.connection as conn
from api.fund_perform_eval import PerformEval
from api import logger

receivers = ['helf1986@qq.com']  # 收件人邮箱账号
# 20180514 新加入资金19800 USDT
initial_amount = ((99960*1.0007) + 19980)/1.007

def clearing():
    '''
    定期进行清结算
    :param interval: 支持两种方式，interval='1day' 每天结算一次，interval='60min' 每小时结算一次
    :param ctime: 指定每天具体时间
    :return:
    '''

    hbaccount = TradeAccount(exchange='hbp', api_key=HBP_ACCESS_KEY,api_secret=HBP_SECRET_KEY, currency='USDT')
    currency = hbaccount.currency.lower()

    # 普通账户数量
    positions = hbaccount.get_positions(source='spot')
    pos_df = to_dataframe(positions)
    # print(pos_df)

    # 借贷账户数量
    positions = hbaccount.get_positions(source='margin')
    pos_df2 = to_dataframe(positions)
    # print(pos_df2)

    pos_df = pos_df.append(pos_df2)

    # 统计总的持仓
    pos_df = pos_df.fillna(0)
    pos_df['netvol'] = pos_df['available'] + pos_df['frozen'] + pos_df['loan'] + pos_df['interest']
    pos_df['price'] = 0

    pos_df = pos_df[pos_df['netvol'] != 0]
    pos_df.index = pos_df['sec_id']
    # print(pos_df)

    # 获取每只币种当前价格
    sec_price = {}
    sec_price[currency] = 1
    sec_ids = list(set(np.unique(pos_df.index)) - set([currency]))
    symbols = [each + currency for each in sec_ids]
    sec_ticks = hbaccount.get_last_ticks(','.join(symbols))
    for each in sec_ticks:
        each_sec = each.sec_id.replace(currency, '')
        sec_price[each_sec] = each.last_price

    # print(sec_price)

    pos_df['price'] = [sec_price[each] for each in pos_df.index]
    pos_df['netamt'] = pos_df['netvol']*pos_df['price']
    # print(pos_df)

    pos_result = pos_df[['account_type', 'available', 'frozen', 'loan', 'interest', 'netvol', 'price', 'netamt']]
    pos_result.columns = ['账户类型', '可用', '冻结', '待还借贷', '待还利息', '净持仓量', '当前价格', '净额']
    # print("当前持仓明细：")
    # print(pos_result)

    total_amount = pos_result['净额'].sum()
    netvalue = total_amount/initial_amount
    # print("当前总持仓额为：", total_amount)
    # print("当前净值为：", netvalue)

    nowstr = time.strftime('%Y-%d-%m %H:%M:%S', time.localtime(time.time()))
    pos_result.to_csv('log/当前持仓明细_' + nowstr + ".csv")

    # 将结果发送给客户
    subject = "BitQuant 净值报告：当前总持仓额=%.4f %s，单位净值=%.4f" %(total_amount, currency, netvalue)

    pos_msg = "最新报告时间：" + nowstr + "\n"
    pos_msg = pos_msg + "当前总持仓额=%.4f %s，单位净值=%.4f \n" % (total_amount, currency, netvalue)
    pos_msg = pos_msg + "\n" + "当前持仓明细：" + "\n"
    for nn in range(len(pos_result)):
        sec_id = pos_result.index[nn]
        data = pos_result.iloc[nn]
        account_type = data['账户类型']
        if account_type == 'spot':
            account_type = '普通账户'
        elif account_type =='margin':
            account_type = '杠杆账户'

        pos_msg = pos_msg + "%s 持有 %s, 可用 %.4f, 冻结 %.4f, 待还借贷 %.4f, 待还利息 %.4f, 净持仓量 %.4f, 当前价格 %.4f, 总金额 %.4f \n" \
                  % (account_type, sec_id, data['可用'], data['冻结'], data['待还借贷'], data['待还利息'], data['净持仓量'], data['当前价格'], data['净额'])
        pos_msg = pos_msg + '\n'

    # 读取最新的邮件列表
    try:
        f = open('monitor/mail_list.txt')
        fdata = f.read()
        receivers = fdata.replace(' ', '').split(',')
    except:
        logger.warn('打开邮件列表失败！\n')

    res = logger.send_mail(subject=subject, content=pos_msg, receivers=receivers)
    if res == True:
        logger.info('净值报告发送成功!')
    else:
        logger.warn('净值报告发送失败!')


if __name__ == '__main__':

    while True:
        # 判断是否达到设定时间，例如0:00
        while True:
            now = time.localtime(time.time())
            nowstr = time.strftime('%Y-%d-%m %H:%M:%S', time.localtime(time.time()))
            print(nowstr)
            # 到达设定时间（每天6:00:00 和 18:00:00），结束内循环
            if (now.tm_hour == 6 or now.tm_hour==18)  and now.tm_min == 0:
                break
            # 不到时间就等31秒之后再次检测
            time.sleep(50)
        # 做正事，一天做一次
        clearing()
        time.sleep(60)

