#!/usr/bin/python
# -*- coding: UTF-8 -*-

import requests #导入requests 模块
from bs4 import BeautifulSoup  #导入BeautifulSoup 模块
import hashlib # 检查重复url
import re
import os

countNum = 1
doc_id = 1
url_dict = {}

class GetHTML():
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}  #给请求指定一个请求头来模拟chrome浏览器
        self.web_url = ''
        self.folder_path = 'C:\\Users\\dlwog\\Pictures\\hi\\pachong'

        print('开始创建文件夹')
        self.mkdir(self.folder_path)  # 创建文件夹
        print('开始切换文件夹')
        os.chdir(self.folder_path)  # 切换路径至上面创建的文件夹

    def get_html(self):
        r = requests.get(self.web_url, headers=self.headers)  # 像目标url地址发送get请求，返回一个response对象
        r.encoding = 'utf-8'

        html_label = BeautifulSoup(r.text, 'lxml')

        find = html_label.find('div', class_="result c-container ", tpl="se_com_default")
        if find is not None:
            time = find.find('span', class_=" newTimeFactor_before_abs m")
            if time is not None:
                time = time.string

            url = find.find('a', target="_blank")['href']

            # 开始进入实际网页

            try:
                re = requests.get(url, headers=self.headers)
            except:
                return True
            hashmd5 = self.check_url(url)

            if hashmd5 in url_dict:
                if url in url_dict[hashmd5]:
                    print("发现重复文档")
                    return True
                else:
                    url_dict[hashmd5].append(url)
            else:
                url_dict[hashmd5] = [url]

            if re.status_code == 200:
                error_check = self.get_txt(re)
                return error_check
            else:
                return True

    def check_url(self, url):
        # 生成一个md5对象
        m1 = hashlib.md5()
        # 使用md5对象里的update方法md5转换
        m1.update(url.encode("utf-8"))
        token = m1.hexdigest()
        return token

    def get_txt(self, r):

        html_text = r.text
        try:
            html_text = html_text.encode(r.encoding)
        except:
            return True

        try:
            html_text = html_text.decode('utf-8')
        except:
            html_text = html_text.decode('gbk')

        html_label = BeautifulSoup(html_text, 'lxml')

        try:
            html_head = html_label.find('head')
            html_title = html_head.find('title').string # 获取网页标题
        except:
            return True

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

        string = html_label.get_text()

        tmp = re.sub(r'\n+', "\n", string)
        tmp1 = re.sub(r'\t*', "", tmp)
        tmp2 = re.sub(r' +', " ", tmp1)
        newstr = re.sub(r' +', " ", tmp2)

        if len(newstr) < 150:
            return True

        tmp = re.sub(r'\n', '', html_title)
        tmp1 = re.sub(r'\t*', "", tmp)
        tmp2 = re.sub(r' +', " ", tmp1)
        html_title = re.sub(r' +', " ", tmp2)

        if html_title[0] == ' ' or html_title[0] == ' ':
            html_title = html_title[1:]
        if html_title[-1] == ' ' or html_title[-1] == ' ':
            html_title = html_title[0:-1]

        self.save_txt(newstr, html_title)
        return False

    def save_txt(self, string, html_title):  ##保存
        file_name = str(doc_id) + ".txt"
        print('开始保存文件')
        f = open(file_name, 'w', encoding='utf-8')
        f.write(html_title + '\n')
        f.write(string)
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

ghtml = GetHTML()  # 创建一个类的实例
f = open("C:\\Users\\dlwog\\Pictures\\hi\\dict.txt.small.txt", 'r', encoding="utf-8")
lines = f.readlines()


for line in lines:
    if countNum % 1000 == 1:
        string = line.split(' ',1)
        print(string[0])
        ghtml.web_url = "https://www.baidu.com/s?wd=" + string[0]
        error_check = ghtml.get_html()  # 执行类中的方法

        if error_check is False:
            countNum = countNum + 1
            doc_id = doc_id + 1
    else:
        countNum = countNum + 1
