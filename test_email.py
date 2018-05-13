'''

import requests

url = "https://wanhupai.com/email"

payload = "[{\"email\":\"rui@wanhupai.com\",\"subject\":\"Test Email From API\",\"content\":\"This is A test from API Call\"},{\"email\":\"ady@wanhupai.com\",\"subject\":\"Test Email From API\",\"content\":\"This is A test from API Call\"}]"
headers = {
    'Content-Type': "application/json",
    'Cache-Control': "no-cache",
    'Postman-Token': "4dc22ae0-06d4-42d9-a49a-cd1e62a623c3"
    }

response = requests.request("POST", url, data=payload, headers=headers)

print(response.text)

'''

# !/usr/bin/python
# -*- coding: UTF-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

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


subject = "BitQuant邮件测试"
content = "2018-05-13 17:32:12 买入 BTC 1.2"
receivers = ['helf1986@qq.com', 'helf@jsfund.cn']  # 收件人邮箱账号，我这边发送给自己
ret = mail(subject, content, receivers)
if ret:
    print("邮件发送成功")
else:
    print("邮件发送失败")