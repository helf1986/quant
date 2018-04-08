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


sms_send_url = "https://feed.shangtalk.com:8443/twilio"

def send_sms(message, phone):

    # 分解号码列表
    phone_list = phone.replace(' ', '').split(',')

    # 依次发送短信通知
    for each_phone in phone_list:
        params = {"region": "86", "phone": each_phone, "message": message}
        url = sms_send_url
        headers = {'Content-Type': 'application/json'}
        postdata = json.dumps(params)
        try:
            response = requests.post(url, postdata, headers=headers, timeout=10)
        except BaseException as e:
            warn("httpPost failed, detail is:%s \n" % response.text)


if __name__ == '__main__':
    # info('asdf','qwerqwer')

    msg = 'hello Q-BTC'
    phone = '13811892804, 18600575531'
    send_sms(msg, phone)
