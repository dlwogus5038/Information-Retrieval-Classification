#encoding=utf-8
import jieba

list = jieba.cut("我是你的爸爸了")
print("/ ".join(list))

import math
print((2 / 2) * (math.log((3 / 2),10) + 1))

import os
path = "C:\\Users\\dlwog\\Pictures\\hi\\pachong\\"
file_list = os.listdir(path)
print(len(file_list))

import json

data = [ { 'a' : 1, 'b' : 2, 'c' : 3, 'd' : 4, 'e' : 5 } ]

json = json.dumps(data, indent=4)
print(json)

'''
import requests #导入requests 模块
from bs4 import BeautifulSoup  #导入BeautifulSoup 模块
import re
import json

f = open("C:\\Users\\dlwog\\Pictures\\hi\\stop_words_test.txt", 'r', encoding="utf-8")
lines = f.readlines()

output = open("C:\\Users\\dlwog\\Pictures\\hi\\stop_words.txt", 'w', encoding="utf-8")
for line in lines:
    string = line.split(' ',3)
    tf = int(string[1])
    new_tf = 1
    while tf >= 10000:
        tf = tf/10
        new_tf = new_tf * 10

    output.write(string[0] + ' ' + str(new_tf) + '\n')

'''