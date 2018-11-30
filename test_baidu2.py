#!/usr/bin/python
# -*- coding: UTF-8 -*-

import requests #导入requests 模块
from bs4 import BeautifulSoup  #导入BeautifulSoup 模块
import re


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}  #给请求指定一个请求头来模拟chrome浏览器
web_url = 'http://www.job1001.com/'
r = requests.get(web_url, headers=headers) #像目标url地址发送get请求，返回一个response对象
html_text = r.text
html_text = html_text.encode(r.encoding)
try:
    html_text = html_text.decode('utf-8')
except:
    html_text = html_text.decode('gbk')
print(r.encoding)
all_a = BeautifulSoup(html_text, 'lxml')  #获取网页中的class为cV68d的所有a标签

find1 = all_a.find_all('script')
for f in find1:
    f.extract()
find2 = all_a.find_all('style')
for f in find2:
    f.extract()

str = all_a.get_text()
tmp = re.sub(r'\n+',"\n",str)
newstr = re.sub(r' +'," ",tmp)
print(newstr)

#105001 58001 43001 35001 28001 16001 10001 4001 https://www.cosumi.net/zh/ http://www.job1001.com/