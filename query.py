from nltk.stem.porter import PorterStemmer
import jieba
import math
import sys
import os
import json
from pathlib import Path

porter_stemmer = PorterStemmer()
word_wij_invert_nk = []
doc_dj_keyword_weight_title_url_time_text = []
term_index_dict = {}


# print("读取 word_wij_invert_nk")
with open('temp\\word_wij_invert_nk.json', 'r', encoding='utf-8-sig') as json_file:
    word_wij_invert_nk = json.load(json_file)

# print("读取 term_index_dict")
with open('temp\\term_index_dict.json', 'r', encoding='utf-8-sig') as json_file:
    term_index_dict = json.load(json_file)

# print("读取 doc_dj_keyword_weight_title_url_time_text")
with open('temp\\doc_dj_keyword_weight_title_url_time_text.json', 'r', encoding='utf-8-sig') as json_file:
    doc_dj_keyword_weight_title_url_time_text = json.load(json_file)

# print("搜索文档")
query_string = "清华大学软件学院"
query_seg_list = jieba.cut_for_search(query_string)

file_list = os.listdir("pachong\\")
doc_num = len(file_list)
query_doc_sim_dict = {}

tmp_list = []
for word in query_seg_list:
    if word not in ['\n', ' ', '\t', ' ']:
        elem = porter_stemmer.stem(word)
        if elem in term_index_dict:
            index = term_index_dict[elem]

            # 从invert_index获取文档列表
            for doc_name in word_wij_invert_nk[index]['invert_index']:
                query_doc_sim_dict[doc_name] = 0
            
            # 创建query的 单词-文档矩阵
            word_wij_invert_nk[index]['wij'][0] = word_wij_invert_nk[index]['wij'][0] + 1
            tmp_list.append(elem)

if tmp_list == []:
    print('没有结果')
    sys.exit()

query_seg_list = tmp_list
mq = 0
for word in query_seg_list: # 计算 mq
    elem = porter_stemmer.stem(word)
    index = term_index_dict[elem]
    if word_wij_invert_nk[index]['wij'][0] > mq:
        mq = word_wij_invert_nk[index]['wij'][0]

dq = 0
for elem in term_index_dict: # 计算 Wkq , dq 然后计算 similarity
    index = term_index_dict[elem]
    if word_wij_invert_nk[index]['wij'][0] == 0:
        idf = math.log((doc_num / word_wij_invert_nk[index]['nk']), 10) + 1
        wkq = idf / 2

        word_wij_invert_nk[index]['wij'][0] = wkq
    else:
        tf = word_wij_invert_nk[index]['wij'][0] / mq
        idf = math.log((doc_num / word_wij_invert_nk[index]['nk']), 10) + 1
        wkq = tf * idf

        word_wij_invert_nk[index]['wij'][0] = wkq

    for doc in query_doc_sim_dict: # 计算 similarity 分子
        query_doc_sim_dict[doc] = query_doc_sim_dict[doc] + ( word_wij_invert_nk[index]['wij'][int(doc)] * word_wij_invert_nk[index]['wij'][0] )

    dq = dq + (word_wij_invert_nk[index]['wij'][0] * word_wij_invert_nk[index]['wij'][0])

dq = dq ** 0.5 # 取根号

for doc in query_doc_sim_dict: # 计算完整的 similarity
    query_doc_sim_dict[doc] = query_doc_sim_dict[doc] / (doc_dj_keyword_weight_title_url_time_text[int(doc)]['dj'] * dq)

doc_list = sorted(query_doc_sim_dict.items(), key= lambda x:x[1] ,reverse=True)

classify_num = 100
classify_list = doc_list[0:classify_num]
classify_num = len(classify_list)

# print(classify_list) # 相似度排序结果

keys = []
classify_dict = {} # 关键词 - 文档编号
doc_vector_dict = {} # 文档编号 - 关键词 wij

for idx in range(0, classify_num):
    keys = keys + doc_dj_keyword_weight_title_url_time_text[int(classify_list[idx][0])]['keywords']
    for word in doc_dj_keyword_weight_title_url_time_text[int(classify_list[idx][0])]['keywords']:
        if word not in ['\n',' ','\t', ' ']:
            index = term_index_dict[word]
            if word in classify_dict:
                classify_dict[word][idx] = word_wij_invert_nk[index]['wij'][int(classify_list[idx][0])]
            else:
                classify_dict[word] = [0] * classify_num
                classify_dict[word][idx] = word_wij_invert_nk[index]['wij'][int(classify_list[idx][0])]
        else:
            print('word Error')

for idx in range(0, classify_num):
    temp_list = []
    for word in classify_dict:
        temp_list.append(classify_dict[word][idx])
    doc_vector_dict[classify_list[idx][0]] = temp_list



keys = list(set(keys))
keys_nbr = len(keys)

# print('动态聚类')

# print('计算重心点')
center_vector = [0] * (keys_nbr)
for idx in range(0, keys_nbr):
    for doc_id in doc_vector_dict:
        center_vector[idx] = center_vector[idx] + doc_vector_dict[doc_id][idx]
    center_vector[idx] = center_vector[idx] / classify_num

'''
test = 0
for idx in range(0, keys_nbr):
    test = test + center_vector[idx]
print(test / keys_nbr) # 0.037671322961006795
'''

# print('计算每个节点和重心点之间的距离')

center_distance_dict = {}
for doc_id in doc_vector_dict:
    center_distance_dict[doc_id] = 0
    for idx in range(0, keys_nbr):
        center_distance_dict[doc_id] = center_distance_dict[doc_id] + (doc_vector_dict[doc_id][idx] - center_vector[idx]) ** 2

for doc_id in doc_vector_dict:
    center_distance_dict[doc_id] = center_distance_dict[doc_id] ** (0.5)
    # print(center_distance_dict[doc_id])


# print('计算每个文档之间的最短距离')
distance_check = [0] * (classify_num * classify_num)
stop_doc = []
count = 0
for id1 in doc_vector_dict:
    stop_doc.append(id1)
    for id2 in doc_vector_dict:
        if id2 not in stop_doc:
            for idx in range(0, keys_nbr):
                distance_check[count] = distance_check[count] + (doc_vector_dict[id1][idx] - doc_vector_dict[id2][idx]) ** 2
            count = count + 1

distance_check = distance_check[0:count]
for idx in range(0, count):
    distance_check[idx] = distance_check[idx] ** (0.5)

min_dist = min(distance_check)
# print('min distance: ' + str(min_dist))
# print('max distance: ' + str(max(distance_check)))

# print('从重心点开始聚类')
class_num = 0
class_verify_list = list(doc_vector_dict.keys())
core_distance = 6
classify_distance = 8
doc_class_dict = {}

center_dict = {}

if min_dist < core_distance:
    core_distance = min_dist
# print('core_distance: ' + str(core_distance))


temp_list = []
temp_vector = [0] * (keys_nbr)
for id in center_distance_dict:
    if center_distance_dict[id] <= core_distance:
        class_verify_list.remove(id)
        temp_list.append(id)
        doc_class_dict[id] = (class_num, doc_vector_dict[id])
        for idx in range(0, keys_nbr):
            temp_vector[idx] = temp_vector[idx] + doc_vector_dict[id][idx]

        del doc_vector_dict[id]

if len(temp_list) != 0:
    for idx in range(0, keys_nbr):
        temp_vector[idx] = temp_vector[idx] / len(temp_list)

    center_dict['key'] = ','.join(temp_list)
    center_dict['value'] = temp_vector
    # print(center_dict['key'])
    # doc_vector_dict[','.join(temp_list)] = temp_vector
    class_num = class_num + 1

'''
center_distance_dict = {}
for doc_id in doc_vector_dict:
    center_distance_dict[doc_id] = 0
    for idx in range(0, keys_nbr):
        center_distance_dict[doc_id] = center_distance_dict[doc_id] + (doc_vector_dict[doc_id][idx] - center_vector[idx]) ** 2

for doc_id in doc_vector_dict:
    center_distance_dict[doc_id] = center_distance_dict[doc_id] ** (0.5)
    print(center_distance_dict[doc_id])
'''
if (min_dist + 2) < classify_distance:
    classify_distance = (min_dist + 2)
# print('classify_distance: '+ str(classify_distance))

while(len(class_verify_list) != 0):
    cur_doc = class_verify_list[0]
    cur_vector = doc_vector_dict[cur_doc]
    min_distance = 10000
    min_node = ''
    for id in doc_vector_dict:
        temp_distance = 0
        if id != cur_doc:
            for idx in range(0, keys_nbr):
                temp_distance = temp_distance + (doc_vector_dict[id][idx] - cur_vector[idx]) ** 2
            temp_distance = temp_distance ** (0.5)
            # print(temp_distance)

            if temp_distance < min_distance:
                min_distance = temp_distance
                min_node = id

    class_verify_list.remove(cur_doc)

    if min_distance >= (classify_distance): # TODO
        doc_class_dict[cur_doc] = (class_num, doc_vector_dict[cur_doc])
        class_num = class_num + 1
    else:
        temp_vector = [0] * (keys_nbr)
        try:
            check_node = min_node.split(',')[0]
        except:
            check_node = min_node
        if check_node in doc_class_dict:
            temp_class = doc_class_dict[check_node][0]
            doc_class_dict[cur_doc] = (temp_class, doc_vector_dict[cur_doc])

            temp_list = []
            for elem in doc_vector_dict:
                if min_node in elem:
                    temp_list = elem.split(',') + [cur_doc]
                    break

            for elem in temp_list:
                for idx in range(0, keys_nbr):
                    temp_vector[idx] = temp_vector[idx] + doc_class_dict[elem][1][idx]

            for idx in range(0, keys_nbr):
                temp_vector[idx] = temp_vector[idx] / len(temp_list)

            doc_vector_dict[','.join(temp_list)] = temp_vector
        else:
            class_verify_list.remove(min_node)
            doc_class_dict[cur_doc] = (class_num, doc_vector_dict[cur_doc])
            doc_class_dict[min_node] = (class_num, doc_vector_dict[min_node])
            for idx in range(0, keys_nbr):
                temp_vector[idx] = doc_vector_dict[cur_doc][idx] + doc_vector_dict[min_node][idx]
                temp_vector[idx] = temp_vector[idx] / 2
            doc_vector_dict[','.join([cur_doc, min_node])] = temp_vector
            class_num = class_num + 1

        del doc_vector_dict[min_node]
        del doc_vector_dict[cur_doc]

if len(center_dict.keys()) != 0:
    doc_vector_dict[center_dict['key']] = center_dict['value']

class_list = list(doc_vector_dict.keys())
class_word = {}

print(class_list)

for doc_id in class_list:
    if ',' in doc_id:
        temp_list = doc_id.split(',')
        temp_dict = {}
        for id in temp_list:
            key_list = doc_dj_keyword_weight_title_url_time_text[int(id)]['keyword_weight']
            for key in key_list:
                if key[0] in temp_dict:
                    temp_dict[key[0]] = temp_dict[key[0]] + key[1]
                else:
                    temp_dict[key[0]] = key[1]
        max_key = max(temp_dict, key=temp_dict.get)

        if max_key in class_word:
            class_word[max_key] = class_word[max_key] + temp_list
        else:
            class_word[max_key] = temp_list
    else:
        keyword = doc_dj_keyword_weight_title_url_time_text[int(doc_id)]['keyword_weight'][0][0]
        if keyword in class_word:
            class_word[keyword].append(doc_id)
        else:
            class_word[keyword] = [doc_id]

print(class_word)

#TODO 关键词 weight로 점수들 다 더해서 점수 제일 높은걸로 分类하기!



# TODO 결과가 하나일떄 오류 뜰수도 있으니 확인해보기!
# TODO 5000개로 바꾸기 (너무 느리면 더 적게 써야될수도..)