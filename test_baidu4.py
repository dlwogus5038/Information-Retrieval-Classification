#!/usr/bin/python
# -*- coding: UTF-8 -*-

import requests #导入requests 模块
from bs4 import BeautifulSoup  #导入BeautifulSoup 模块
import re
import os
import time

class GetHTML():
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}  #给请求指定一个请求头来模拟chrome浏览器
        self.web_url = 'https://www.baidu.com/s?wd=C++'

    def get_html(self):
        r = requests.get(self.web_url, headers=self.headers)  # 像目标url地址发送get请求，返回一个response对象
        r.encoding = 'utf-8'
        all_a = BeautifulSoup(r.text, 'lxml')  # 获取网页中的class为cV68d的所有a标签
        finds = all_a.find_all('div', class_="result c-container ", tpl="se_com_default")
        for find in finds:
            if find is not None:
                print(find.find('span', class_=" newTimeFactor_before_abs m"))
                url = find.find('a', target="_blank")['href']

                re = requests.get(url, headers=self.headers)
                re.encoding = 'utf-8'
                if "baike.baidu.com" in re.url:
                    continue
                else:
                    print(re.url)
                    break


beauty = GetHTML()  #创建一个类的实例
beauty.get_html()  #执行类中的方法