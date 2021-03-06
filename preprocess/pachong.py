#!/usr/bin/python
# -*- coding: UTF-8 -*-

import requests #导入requests 模块
from bs4 import BeautifulSoup  #导入BeautifulSoup 模块
import hashlib # 检查重复url
import re
import os
import json

countNum = 1
doc_id = 1
url_dict = {}

class GetHTML():
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}  #给请求指定一个请求头来模拟chrome浏览器
        self.web_url = ''
        self.folder_path = 'pachong'

        print('创建文件夹')
        self.mkdir(self.folder_path)  # 创建文件夹
        print('切换路径')
        os.chdir(self.folder_path)  # 切换路径至上面创建的文件夹

    def get_html(self):
        r = requests.get(self.web_url, headers=self.headers)  # 像目标url地址发送get请求，返回一个response对象
        r.encoding = 'utf-8'

        html_label = BeautifulSoup(r.text, 'lxml')

        doc_nbr = 0

        find_list = html_label.find_all('div', class_="result c-container ", tpl="se_com_default")
        for find in find_list:
            if doc_nbr == 3:
                break
            if find is not None:
                time = find.find('span', class_=" newTimeFactor_before_abs m")
                if time is not None:
                    time = time.string

                title = find.find('h3', class_="t")
                title = title.find('a')
                title = title.text

                url = find.find('a', target="_blank")['href']

                # 开始进入实际网页

                try:
                    re = requests.get(url, headers=self.headers)
                    url = re.url
                except:
                    continue
                hashmd5 = self.check_url(url)
                # print(hashmd5)

                if hashmd5 in url_dict:
                    if url in url_dict[hashmd5]:
                        print("发现重复文档 title: " + title)
                        continue
                    else:
                        url_dict[hashmd5].append(url)
                else:
                    url_dict[hashmd5] = [url]

                if re.status_code == 200:
                    error_check = self.get_txt(re, title, url, time)
                    if error_check == True:
                        continue
                    else:
                        doc_nbr = doc_nbr + 1
                else:
                    continue
        return doc_nbr

    def check_url(self, url):
        # 生成一个md5对象
        m1 = hashlib.md5()
        # 使用md5对象里的update方法md5转换
        m1.update(url.encode("utf-8"))
        token = m1.hexdigest()
        return token

    def get_txt(self, r, title, url, time):

        html_text = r.text
        try:
            html_text = html_text.encode(r.encoding)
        except:
            return True

        try:
            html_text = html_text.decode('utf-8')
        except:
            try:
                html_text = html_text.decode('gbk')
            except:
                return True

        html_label = BeautifulSoup(html_text, 'lxml')

        html_title = title

        find1 = html_label.find_all('script')
        for f in find1:
            f.extract()
        find2 = html_label.find_all('style')
        for f in find2:
            f.extract()
        find3 = html_label.find_all(class_=re.compile('header'))
        for f in find3:
            f.extract()
        find4 = html_label.find_all(class_=re.compile('nav'))
        for f in find4:
            f.extract()
        find5 = html_label.find_all(class_=re.compile('footer'))
        for f in find5:
            f.extract()
        find6 = html_label.find_all(id=re.compile('header'))
        for f in find6:
            f.extract()
        find7 = html_label.find_all(id=re.compile('nav'))
        for f in find7:
            f.extract()
        find8 = html_label.find_all(id=re.compile('footer'))
        for f in find8:
            f.extract()
        find9 = html_label.find_all('header')
        for f in find9:
            f.extract()

        string = html_label.get_text()

        newstr = self.get_real_str(string)

        if len(newstr) < 150:
            return True

        html_title = self.get_real_str(html_title)
        time = str(time)

        if html_title[0] == ' ' or html_title[0] == ' ':
            html_title = html_title[1:]
        if html_title[-1] == ' ' or html_title[-1] == ' ':
            html_title = html_title[0:-1]

        self.save_txt(newstr, html_title, url, time)
        return False

    def save_txt(self, string, html_title, url, time):  ##保存
        global  doc_id
        file_name = str(doc_id) + ".txt"
        # print('开始保存文件')
        f = open(file_name, 'w', encoding='utf-8')
        f.write(html_title + '\n')
        f.write(url + '\n')
        f.write(time + '\n')
        f.write(string)
        print(file_name, '文件保存成功！')
        f.close()
        doc_id = doc_id + 1

    def mkdir(self, path):  ##这个函数创建文件夹
        path = path.strip()
        isExists = os.path.exists(path)
        if not isExists:
            print('创建名字叫做', path, '的文件夹')
            os.makedirs(path)
            print('创建成功！')
        else:
            print(path, '文件夹已存在，不再创建')

    def get_real_str(self, string):
        tmp = re.sub(r'\n', '', string)
        tmp1 = re.sub(r'\t*', "", tmp)
        tmp2 = re.sub(r' +', " ", tmp1)
        new_str = re.sub(r' +', " ", tmp2)
        return new_str

ghtml = GetHTML()  # 创建一个类的实例
f = open("../dict/dict.txt.small.txt", 'r', encoding="utf-8")
lines = f.readlines()


for line in lines:
    if countNum % 65 == 1:
        string = line.split(' ',1)
        print(string[0])
        ghtml.web_url = "https://www.baidu.com/s?wd=" + string[0]
        doc_nbr = ghtml.get_html()  # 执行类中的方法

        countNum = countNum + doc_nbr
    else:
        countNum = countNum + 1
