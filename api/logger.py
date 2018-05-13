# -*- coding: utf-8 -*-
# __author__ = 'lie.tian'
# create date = 2016/12/12

import datetime
import time
import os
import traceback
import json
import urllib
import urllib.parse
import urllib.request
import requests

LOGFILE = "log/log.log"


def get_vals(vs):
    vals = ''
    for v in range(0,len(vs)):
        if v ==0:
            vals += str(vs[v])
        else:
            vals += '\t'+str(vs[v])
    return vals


def info(*info1):
    exec_info = str(datetime.datetime.now())+'\tINFO\t'+get_vals(info1) + '\n'
    print (exec_info)
    logfile = LOGFILE
    f = open(logfile, "a")
    f.write(exec_info)


def debug(*debug1):
    exec_info = str(datetime.datetime.now())+'\tDEBUG\t'+get_vals(debug1) + '\n'
    print (exec_info)
    logfile = logfile = LOGFILE
    f = open(logfile, "a")
    f.write(exec_info)


def warn(*warn1):
    exec_info = str(datetime.datetime.now())+'\tWARN\t'+get_vals(warn1) + '\n'
    print (exec_info)
    logfile = logfile = LOGFILE
    f = open(logfile, "a")
    f.write(exec_info)


def error(*error1):
    try:
        exec_info = str(datetime.datetime.now())+'\tERROR\t'+get_vals(error1) + '\n'
        raise Exception(exec_info)
        logfile = LOGFILE
        f = open(logfile, "a")
        f.write(exec_info)
    except Exception as e:
        traceback.print_exc()
        os._exit(1)


SMS_URL = "https://feed.shangtalk.com:8443/twilio"

def send_sms(message, phone):

    # 分解号码列表
    phone_list = phone.replace(' ', '').split(',')

    # 依次发送短信通知
    for each_phone in phone_list:
        params = {"region": "86", "phone": each_phone, "message": message}
        url = SMS_URL
        headers = {'Content-Type': 'application/json'}
        postdata = json.dumps(params)
        try:
            response = requests.post(url, postdata, headers=headers, timeout=10)
        except BaseException as e:
            warn("httpPost failed, detail is:%s \n" % response.text)


import smtplib
from email.mime.text import MIMEText

SMTP = "smtp.qq.com"
PORT = 465
SENDER = 'helf1986@qq.com'  # 发件人邮箱账号
PASSWORD = 'jrhlojstnqjvcbcg'  # 发件人邮箱密码

def mail(subject, content, receivers):
    ret = True
    try:
        msg = MIMEText(content, 'plain', 'utf-8')
        msg['From'] = SENDER     # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['To'] = ";".join(receivers)                       # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = subject                                # 邮件的主题，也可以说是标题

        server = smtplib.SMTP_SSL(SMTP, PORT)                   # 发件人邮箱中的SMTP服务器，端口是25
        server.login(SENDER, PASSWORD)                           # 括号中对应的是发件人邮箱账号、邮箱密码
        server.sendmail(SENDER, receivers, msg.as_string())   # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
    except Exception:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
        ret = False
    return ret


if __name__ == '__main__':
    # info('asdf','qwerqwer')

    '''
    msg = 'hello Q-BTC'
    phone = '13811892804, 18600575531'
    send_sms(msg, phone)
    '''

    subject = "BitQuant 交易信号测试"
    content = "2018-05-13 17:32:12 买入 1.2 BTC, 买入价格9123.4, 手续费0.0024 BTC"
    receivers = ['helf1986@qq.com', 'zhaoyu@zhenfund.com', 'ady.chen@icloud.com']  # 收件人邮箱账号，我这边发送给自己
    ret = mail(subject, content, receivers)
    if ret:
        print("邮件发送成功")
    else:
        print("邮件发送失败")