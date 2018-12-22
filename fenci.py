#encoding=utf-8
from nltk.stem.porter import PorterStemmer
import jieba
import math
import sys
import os
import json
from pathlib import Path
from jieba import analyse


def mkdir(path):  ##这个函数创建文件夹
    path = path.strip()
    isExists = os.path.exists(path)
    if not isExists:
        print('创建名字叫做', path, '的文件夹')
        os.makedirs(path)
        print('创建成功！')
    else:
        print(path, '文件夹已存在，不再创建')

mkdir('fenci')
mkdir('temp')

# 英文获取词干
porter_stemmer = PorterStemmer()
path = "pachong\\"
new_path = "fenci\\"
doc_num = 0 # 文档个数
doc_id = 0
term_doc_dict = {}
invert_index = {}
mj_list = []
nk_dict = {}
dj_len_list = []
keyword_doc_dict = {}
keyword_weight_dict = {}
doc_text_dict = {}
doc_time_dict = {}
doc_title_dict = {}
doc_url_dict = {}

file_list = os.listdir(path)
doc_num = len(file_list)

extract_words = analyse.extract_tags

print("创建单词-文档矩阵,倒排索引列表，文档长度列表")
for file_name in file_list:
    file_object = open(path + file_name, encoding='utf-8-sig')
    doc_id = int(file_name[0 : file_name.find('.txt')])

    all_the_text = file_object.read()

    divide_idx = all_the_text.find('\n')
    html_title = all_the_text[0: divide_idx]
    all_the_text = all_the_text[divide_idx + 1:]

    divide_idx = all_the_text.find('\n')
    html_url = all_the_text[0: divide_idx]
    all_the_text = all_the_text[divide_idx + 1:]

    divide_idx = all_the_text.find('\n')
    html_time = all_the_text[0: divide_idx]
    all_the_text = all_the_text[divide_idx + 1:]

    all_the_text = html_title + all_the_text




    doc_text_dict[doc_id] = all_the_text
    doc_title_dict[doc_id] = html_title
    doc_url_dict[doc_id] = html_url
    doc_time_dict[doc_id] = html_time

    title_list = []
    for elem in jieba.cut(html_title):
        if elem not in ['\n',' ','\t', ' ']:
            title_list.append(elem)

    # 开始抽取每个文档的关键词
    keyword_weight = extract_words(all_the_text, topK=20, withWeight=True)

    keyword_list = []
    for elem in keyword_weight:
        keyword_list.append(elem[0])

    for elem in jieba.cut(html_title):
        if elem not in ['\n',' ','\t', ' '] and elem not in keyword_list:
            keyword_list.append(elem)
            keyword_weight.append((elem, 0.2))

    keyword_doc_dict[doc_id] = keyword_list
    keyword_weight_dict[doc_id] = keyword_weight
    # keyword_doc_dict[doc_id] = list(set(keyword_doc_dict[doc_id]))

    temp_list = []
    for elem in keyword_doc_dict[doc_id]:
        word = porter_stemmer.stem(elem)
        temp_list.append(word)
    keyword_doc_dict[doc_id] = temp_list

    temp_list = []
    for elem in keyword_weight_dict[doc_id]:
        word = porter_stemmer.stem(elem[0])
        temp_list.append((word, elem[1]))
    temp_list = sorted(temp_list, key= lambda x:x[1] ,reverse=True)
    keyword_weight_dict[doc_id] = temp_list

    # 开始分词
    seg_list = jieba.cut(all_the_text)

    f = open(new_path + file_name, 'w', encoding='utf-8')

    word_index = 0
    for word in seg_list:
        w = porter_stemmer.stem(word)
        if w not in ['\n',' ','\t', ' '] and w in keyword_doc_dict[doc_id]:
            # 英文获取词干
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
stop_words = open("dict\\stop_words.txt", 'r', encoding="utf-8-sig")
lines = stop_words.readlines()
for line in lines:
    try:
        words = line.split(' ', 1)
        word = porter_stemmer.stem(words[0])
        for ind in range(1, doc_num+1):
            term_doc_dict[word][ind] = term_doc_dict[word][ind] / int(words[1][:-1])
    except:
        print("没有 " + line)
        continue


# 求 nk 和 mj （为了求tf-idf权值）
print("计算nk,mj,dj_len")
mj_list = [0]*(doc_num + 1)
for key in term_doc_dict:
    nk_dict[key] = 0
    for index in range(1, doc_num+1):
        if term_doc_dict[key][index] > mj_list[index]:
            mj_list[index] = term_doc_dict[key][index]
        if term_doc_dict[key][index] != 0:
            nk_dict[key] = nk_dict[key] + 1


print("计算tf，idf, wkj和dj_len")
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

print("取根号dj_len")
for index in range(1, doc_num+1):
    dj_len_list[index] = dj_len_list[index] ** 0.5

print("筛选关键词")
del_keyword = "!\"#@$%^&*()_-+=\\|][}{\';:/?.>,<、，。‘“；：、|】}【{——）（……￥！·~`《》？”’`"
for doc_id in keyword_weight_dict:
    temp_list = []
    for elem in keyword_weight_dict[doc_id]:
        elem_len = len(elem[0])
        count = 0
        for ch in elem[0]:
            if ch in del_keyword:
                count = count + 1

        #if count == elem_len:
        #    print(str(doc_id) + " delete " + elem[0])
        #else:
        #    temp_list.append(elem)

        if count != elem_len:
            temp_list.append(elem)
    keyword_weight_dict[doc_id] = temp_list

print("保存数据")
index = 0
term_index_dict = {}
word_wij_invert_nk = [None] * len(term_doc_dict)
doc_dj_keyword_weight_title_url_time_text = [None] * (len(keyword_doc_dict) + 1)
for elem in term_doc_dict:
    temp_dict = {}
    temp_dict['word'] = elem
    temp_dict['wij'] = term_doc_dict[elem]
    temp_dict['invert_index'] = invert_index[elem]
    temp_dict['nk'] = nk_dict[elem]
    word_wij_invert_nk[index] = temp_dict

    term_index_dict[elem] = index
    index = index + 1

for id in keyword_doc_dict:
    temp_dict = {}
    temp_dict['doc_id'] = id
    temp_dict['dj'] = dj_len_list[int(id)]
    temp_dict['keywords'] = keyword_doc_dict[id]
    temp_dict['keyword_weight'] = keyword_weight_dict[id]
    temp_dict['title'] = doc_title_dict[id]
    temp_dict['url'] = doc_url_dict[id]
    temp_dict['time'] = doc_time_dict[id]
    temp_dict['text'] = doc_text_dict[id]
    doc_dj_keyword_weight_title_url_time_text[int(id)] = temp_dict

print("保存 word_wij_invert_nk")
with open('temp\\word_wij_invert_nk.json', 'w', encoding='utf-8-sig') as json_file:
    json.dump(word_wij_invert_nk, json_file, ensure_ascii=False)

print("保存 term_index_dict")
with open('temp\\term_index_dict.json', 'w', encoding='utf-8-sig') as json_file:
    json.dump(term_index_dict, json_file, ensure_ascii=False)

print("保存 doc_dj_keyword_weight_title_url_time_text")
with open('temp\\doc_dj_keyword_weight_title_url_time_text.json', 'w', encoding='utf-8-sig') as json_file:
    json.dump(doc_dj_keyword_weight_title_url_time_text, json_file, ensure_ascii=False)

print("记录单词")
check_dict = open(new_path + 'check_dict.txt', 'w', encoding='utf-8-sig') # 检查字典中有没有乱码
for item in term_doc_dict:
    check_dict.write(item + ' ')
check_dict.close()

print("记录关键词")
check_dict = open(new_path + 'keyword_dict.txt', 'w', encoding='utf-8-sig') # 检查关键词中有没有乱码
for id in range(1, len(keyword_weight_dict)+1):
    for elem in keyword_weight_dict[str(id)]:
        check_dict.write(elem[0] + ' ')
    check_dict.write('\n')
check_dict.close()