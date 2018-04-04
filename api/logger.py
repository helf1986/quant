# -*- coding: utf-8 -*-
# __author__ = 'lie.tian'
# create date = 2016/12/12

import datetime
import os
import traceback
import json
import urllib
import urllib.parse
import urllib.request
import requests

LOGFILE = "log\\log.log"


def get_vals(vs):
    vals = ''
    for v in range(0,len(vs)):
        if v ==0:
            vals += str(vs[v])
        else:
            vals += '\t'+str(vs[v])
    return vals


def info(*info1):
    exec_info = str(datetime.datetime.now())+'\tINFO\t'+get_vals(info1)
    print (exec_info)
    logfile = LOGFILE
    f = open(logfile, "a")
    f.write(exec_info)


def debug(*debug1):
    exec_info = str(datetime.datetime.now())+'\tDEBUG\t'+get_vals(debug1)
    print (exec_info)
    logfile = logfile = LOGFILE
    f = open(logfile, "a")
    f.write(exec_info)


def warn(*warn1):
    exec_info = str(datetime.datetime.now())+'\tWARN\t'+get_vals(warn1)
    print (exec_info)
    logfile = logfile = LOGFILE
    f = open(logfile, "a")
    f.write(exec_info)


def error(*error1):
    try:
        exec_info = str(datetime.datetime.now())+'\tERROR\t'+get_vals(error1)
        raise Exception(exec_info)
        logfile = logfile = LOGFILE
        f = open(logfile, "a")
        f.write(exec_info)
    except Exception as e:
        traceback.print_exc()
        os._exit(1)


sms_send_url = "https://feed.shangtalk.com:8443/twilio"

def send_sms(message, phone):
    params = {"region": "86", "phone": phone, "message": message}

    url = sms_send_url
    headers = {'Content-Type': 'application/json'}
    postdata = json.dumps(params)
    response = requests.post(url, postdata, headers=headers, timeout=10)
    try:

        if response.status_code == 200:
            return response.content
        else:
            return
    except BaseException as e:
        print("httpPost failed, detail is:%s,%s" % (response.text, e))
        return


if __name__ == '__main__':
    info('asdf','qwerqwer')