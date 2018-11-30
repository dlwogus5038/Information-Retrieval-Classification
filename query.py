from nltk.stem.porter import PorterStemmer
import jieba
import math
import sys
import os
import json
from pathlib import Path

term_doc_dict = {}
invert_index = {}
nk_dict = {}
mj_list = []
dj_len_list = []
keyword_doc_dict = {}
title_doc_dict = {}

print("读取 term_doc_dict")
with open('C:\\Users\\dlwog\\Pictures\\hi\\term_doc_dict.json', 'r', encoding='utf-8') as json_file:
    term_doc_dict = json.load(json_file)

print("读取 invert_index")
with open('C:\\Users\\dlwog\\Pictures\\hi\\invert_index.json', 'r', encoding='utf-8') as json_file:
    invert_index = json.load(json_file)

print("读取 nk_dict")
with open('C:\\Users\\dlwog\\Pictures\\hi\\nk_dict.json', 'r', encoding='utf-8') as json_file:
    nk_dict = json.load(json_file)

print("读取 mj_list")
with open('C:\\Users\\dlwog\\Pictures\\hi\\mj_list.json', 'r', encoding='utf-8') as json_file:
    mj_list = json.load(json_file)

print("读取 dj_len_list")
with open('C:\\Users\\dlwog\\Pictures\\hi\\dj_len_list.json', 'r', encoding='utf-8') as json_file:
    dj_len_list = json.load(json_file)

print("读取 keyword_doc_dict")
with open('C:\\Users\\dlwog\\Pictures\\hi\\keyword_doc_dict.json', 'r', encoding='utf-8') as json_file:
    keyword_doc_dict = json.load(json_file)

print("读取 title_doc_dict")
with open('C:\\Users\\dlwog\\Pictures\\hi\\title_doc_dict.json', 'r', encoding='utf-8') as json_file:
    title_doc_dict = json.load(json_file)

for elem in title_doc_dict: # 把题目做分词之后，把分好的单词放在关键词字典里
    seg_list = jieba.cut(title_doc_dict[elem])
    for seg in seg_list:
        keyword_doc_dict[elem].append(seg)

    keyword_doc_dict[elem] = list(set(keyword_doc_dict[elem])) # 去重

print("开始搜索文档")
query_string = "开始搜索文档"
query_seg_list = jieba.cut_for_search(query_string)


doc_num = len(mj_list) - 1
query_doc_sim_dict = {}

tmp_list = []
for elem in query_seg_list:
    if elem in invert_index: # 从invert_index获取文档列表
        for doc_name in invert_index[elem]:
            query_doc_sim_dict[doc_name] = 0

    if elem in term_doc_dict: # 创建query的 单词-文档矩阵
        term_doc_dict[elem][0] = term_doc_dict[elem][0] + 1

    tmp_list.append(elem)

query_seg_list = tmp_list
mq = 0
for elem in query_seg_list: # 计算 mq
    if term_doc_dict[elem][0] > mq:
        mq = term_doc_dict[elem][0]

dq = 0
for elem in term_doc_dict: # 计算 Wkq , dq 然后计算 similarity
    if term_doc_dict[elem][0] == 0: # 如果程序执行速度太慢了，可以不考虑 == 0 的情况，这时候 for 需要用 query_seg_list, 而不是 term_doc_dict
        idf = math.log((doc_num / nk_dict[elem]), 10) + 1
        wkq = idf / 2

        term_doc_dict[elem][0] = wkq
    else:
        tf = term_doc_dict[elem][0] / mq
        idf = math.log((doc_num / nk_dict[elem]), 10) + 1
        wkq = tf * idf

        term_doc_dict[elem][0] = wkq

    for doc in query_doc_sim_dict: # 计算 similarity 分子
        query_doc_sim_dict[doc] = query_doc_sim_dict[doc] + ( term_doc_dict[elem][int(doc)] * term_doc_dict[elem][0] )

    dq = dq + (term_doc_dict[elem][0] * term_doc_dict[elem][0])

dq = dq ** 0.5 # 取根号

for doc in query_doc_sim_dict: # 计算完整的 similarity
    query_doc_sim_dict[doc] = query_doc_sim_dict[doc] / (dj_len_list[int(doc)] * dq)

list = sorted(query_doc_sim_dict.items(), key= lambda x:x[1] ,reverse=True)

print(list[0:20]) # 相似度排序结果