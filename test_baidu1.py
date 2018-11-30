import requests #导入requests 模块
from bs4 import BeautifulSoup  #导入BeautifulSoup 模块

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}  #给请求指定一个请求头来模拟chrome浏览器
web_url = 'https://www.baidu.com/s?wd=程序员'
r = requests.get(web_url, headers=headers) #像目标url地址发送get请求，返回一个response对象
r.encoding = 'utf-8'
all_a = BeautifulSoup(r.text, 'lxml').find_all('head')  #获取网页中的class为cV68d的所有a标签
print(all_a)