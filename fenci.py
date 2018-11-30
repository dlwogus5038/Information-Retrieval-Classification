#encoding=utf-8
from nltk.stem.porter import PorterStemmer
import jieba
import math
import sys
import os
import json
from pathlib import Path
from jieba import analyse

# 英文获取词干
porter_stemmer = PorterStemmer()
path = "C:\\Users\\dlwog\\Pictures\\hi\\pachong\\"
new_path = "C:\\Users\\dlwog\\Pictures\\hi\\fenci\\"
doc_num = 0 # 文档个数
doc_id = 0
term_doc_dict = {}
invert_index = {}
mj_list = []
nk_dict = {}
dj_len_list = []
keyword_doc_dict = {}
title_doc_dict = {}

file_list = os.listdir(path)
doc_num = len(file_list)

extract_words = analyse.extract_tags

print("开始创建单词-文档矩阵,倒排索引列表，文档长度列表")
for file_name in file_list:
    file_object = open(path + file_name, encoding='utf-8-sig')
    doc_id = int(file_name[0 : file_name.find('.txt')])

    all_the_text = file_object.read()
    html_title = all_the_text[0: all_the_text.find('\n')]
    title_doc_dict[doc_id] = html_title

    # 开始抽取每个文档的关键词
    keywords = extract_words(all_the_text)
    keyword_doc_dict[doc_id] = keywords

    # 开始分词
    seg_list = jieba.cut(all_the_text)

    f = open(new_path + file_name, 'w', encoding='utf-8')

    word_index = 0
    for w in seg_list:
        if w not in ['\n',' ','\t', ' ']:
            # 英文获取词干
            w = porter_stemmer.stem(w)
            if w in term_doc_dict:
                term_doc_dict[w][doc_id] = term_doc_dict[w][doc_id] + 1
            else:
                term_doc_dict[w] = [0]*( doc_num + 1 )
                term_doc_dict[w][doc_id] = term_doc_dict[w][doc_id] + 1

            if w in invert_index:
                if doc_id in invert_index[w]:
                    invert_index[w][doc_id].append((word_index, word_index + len(w)))  # 单词开始位置 , 单词结束位置
                else:
                    invert_index[w][doc_id] = []
                    invert_index[w][doc_id].append((word_index, word_index + len(w)))  # 单词开始位置 , 单词结束位置
            else:
                invert_index[w] = {}
                invert_index[w][doc_id] = []
                invert_index[w][doc_id].append((word_index, word_index + len(w))) # 单词开始位置 , 单词结束位置

            f.write(w + '\n')

        word_index = word_index + len(w)

    f.close()
    file_object.close()

print("停用词处理")
stop_words = open("C:\\Users\\dlwog\\Pictures\\hi\\stop_words.txt", 'r', encoding="utf-8-sig")
lines = stop_words.readlines()
for line in lines:
    try:
        words = line.split(' ', 1)
        words[0] = porter_stemmer.stem(words[0])
        for ind in range(1, doc_num+1):
            term_doc_dict[words[0]][ind] = term_doc_dict[words[0]][ind] / int(words[1][:-1])
    except:
        print("没有 " + line)
        continue


# 求 nk 和 mj （为了求tf-idf权值）
print("开始计算nk,mj,dj_len")
mj_list = [0]*(doc_num + 1)
for key in term_doc_dict:
    nk_dict[key] = 0
    for index in range(1, doc_num+1):
        if term_doc_dict[key][index] > mj_list[index]:
            mj_list[index] = term_doc_dict[key][index]
        if term_doc_dict[key][index] != 0:
            nk_dict[key] = nk_dict[key] + 1


print("开始计算tf，idf, wkj和dj_len")
dj_len_list = [0]*(doc_num + 1)
for key in term_doc_dict:
    for index in range(1, doc_num+1):
        if term_doc_dict[key][index] == 0:
            wkj = 0
        else:
            tf = term_doc_dict[key][index] / mj_list[index]
            idf = math.log((doc_num / nk_dict[key]),10) + 1
            wkj = tf * idf

        term_doc_dict[key][index] = wkj
        dj_len_list[index] = dj_len_list[index] + (wkj * wkj)

print("开始取根号dj_len")
for index in range(1, doc_num+1):
    dj_len_list[index] = dj_len_list[index] ** 0.5


print("保存 term_doc_dict")
with open('C:\\Users\\dlwog\\Pictures\\hi\\term_doc_dict.json', 'w', encoding='utf-8') as json_file:
    json.dump(term_doc_dict, json_file, ensure_ascii=False)

print("保存 invert_index")
with open('C:\\Users\\dlwog\\Pictures\\hi\\invert_index.json', 'w', encoding='utf-8') as json_file:
    json.dump(invert_index, json_file, ensure_ascii=False)

print("保存 nk_dict")
with open('C:\\Users\\dlwog\\Pictures\\hi\\nk_dict.json', 'w', encoding='utf-8') as json_file:
    json.dump(nk_dict, json_file, ensure_ascii=False)

print("保存 mj_list")
with open('C:\\Users\\dlwog\\Pictures\\hi\\mj_list.json', 'w', encoding='utf-8') as json_file:
    json.dump(mj_list, json_file, ensure_ascii=False)

print("保存 dj_len_list")
with open('C:\\Users\\dlwog\\Pictures\\hi\\dj_len_list.json', 'w', encoding='utf-8') as json_file:
    json.dump(dj_len_list, json_file, ensure_ascii=False)

print("保存 keyword_doc_dict")
with open('C:\\Users\\dlwog\\Pictures\\hi\\keyword_doc_dict.json', 'w', encoding='utf-8') as json_file:
    json.dump(keyword_doc_dict, json_file, ensure_ascii=False)

print("保存 title_doc_dict")
with open('C:\\Users\\dlwog\\Pictures\\hi\\title_doc_dict.json', 'w', encoding='utf-8') as json_file:
    json.dump(title_doc_dict, json_file, ensure_ascii=False)


print("开始记录单词")
check_dict = open(new_path + 'check_dict.txt', 'w', encoding='utf-8') # 检查字典中有没有乱码
for item in term_doc_dict:
    check_dict.write(item + ' ')
check_dict.close()