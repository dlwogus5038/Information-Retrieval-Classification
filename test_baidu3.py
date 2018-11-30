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
        self.web_url = 'https://baike.baidu.com/item/%E8%B5%9B%E4%BC%9A/4596834'
        self.folder_path = 'C:\\Users\\dlwog\\Pictures\\hi'

        print('开始创建文件夹')
        self.mkdir(self.folder_path)  # 创建文件夹
        print('开始切换文件夹')
        os.chdir(self.folder_path)  # 切换路径至上面创建的文件夹

    def get_html(self):
        r = requests.get(self.web_url, headers=self.headers)  # 像目标url地址发送get请求，返回一个response对象
        r.encoding = 'utf-8'
        all_a = BeautifulSoup(r.text, 'lxml')  # 获取网页中的class为cV68d的所有a标签
        find1 = all_a.find_all('script')
        for f in find1:
            f.extract()
        find2 = all_a.find_all('style')
        for f in find2:
            f.extract()
        find3 = all_a.find_all(class_=re.compile('header'))  ########################################
        for f in find3:  ########################################
            f.extract()  ########################################
        find4 = all_a.find_all(class_=re.compile('navbar'))  ########################################
        for f in find4:  ########################################
            f.extract()  ########################################
        find5 = all_a.find_all(class_=re.compile('footer'))  ########################################
        for f in find5:  ########################################
            f.extract()  ########################################

        str = all_a.get_text()

        tmp = re.sub(r'\n+', "\n", str)
        tmp1 = re.sub(r'\t*', "", tmp)
        newstr = re.sub(r' +', " ", tmp1)

        self.save_txt(newstr)

    def save_txt(self, str):  ##保存图片
        print('开始保存图片...')
        file_name = '1.txt'
        print('开始保存文件')
        f = open(file_name, 'w', encoding='utf-8')
        f.write(str)
        print(file_name, '文件保存成功！')
        f.close()

    def mkdir(self, path):  ##这个函数创建文件夹
        path = path.strip()
        isExists = os.path.exists(path)
        if not isExists:
            print('创建名字叫做', path, '的文件夹')
            os.makedirs(path)
            print('创建成功！')
        else:
            print(path, '文件夹已经存在了，不再创建')

beauty = GetHTML()  #创建一个类的实例
beauty.get_html()  #执行类中的方法