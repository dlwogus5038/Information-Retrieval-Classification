from django.shortcuts import render
from IR import settings
import jieba
import math
import os

search_result = []
cluster_result = []
cur_search = []
page_num = "1"
page_list = []
page_len = 1
cur_class = ""


# Create your views here.
def index(request):
    return render(request, 'index.html', {'sentence' : ""})


def show_cluster(request):
    global cur_class
    global page_num
    global page_list
    global cur_search
    global page_len
    cur_class = request.GET.get('show_cluster')
    search_sentence = request.GET.get('sentence')

    page_list = []
    page_num = "1"

    if cur_class == "ALL":
        cur_search = search_result[0]
    else:
        cur_list = []
        for elem in search_result[1]:
            if elem[0] == cur_class:
                cur_list = elem[2]

        temp_list = []
        for doc_id in cur_list:
            for elem in search_result[0]:
                if str(elem[5]) == doc_id:
                    temp_list.append(elem)
                    break
        cur_search = temp_list

    if len(cur_search) == 0:
        page_len = 1
    else:
        page_len = int((len(cur_search) - 1) / 10) + 1

    for i in range(1, page_len + 1):
        page_list.append(str(i))

    doc_list = cur_search[0: 10]

    return render(request, 'index.html',
                  {'sentence': search_sentence, 'search_result': doc_list, 'cluster_result': search_result[1],
                   "page": page_num, "page_list": page_list, "cur_class": cur_class})


def page(request):
    global search_result
    global cluster_result
    global cur_search
    search_sentence = request.GET.get('sentence')
    page_num = request.GET.get('page')
    cluster = request.GET.get('show_cluster')

    doc_list = cur_search[(int(page_num) * 10) - 10 : (int(page_num) * 10)]
    return render(request, 'index.html',
                  {'sentence': search_sentence, 'search_result': doc_list, 'cluster_result': search_result[1],
                   "page" : page_num, "page_list" : page_list, "cur_class" : cluster})


def search(request):
    global search_result
    global cluster_result
    global page_list
    global page_len
    global cur_class
    global cur_search
    search_sentence = request.GET.get('sentence')
    query_seg_list = jieba.cut_for_search(search_sentence)
    seg_list = []
    for elem in query_seg_list:
        seg_list.append(elem)

    result = search_cluster(seg_list)
    if result[0] == [] and result[1] == []:
        return render(request, 'index.html', {'sentence': "", "page" : "1", "page_list" : []})
    int_id = []
    for elem in result[0]:
        int_id.append(int(elem))

    dtttu = settings.collection2.find({"doc_id":{"$in":int_id}}, projection=['doc_id','title','time','text','url'])
    search_result = make_doc_list(dtttu, result, seg_list)

    page_list = []
    if len(search_result[0]) == 0:
        page_len = 1
    else:
        page_len = int((len(search_result[0]) - 1) / 10) + 1

    for i in range(1,page_len+1):
        page_list.append(str(i))

    doc_list = search_result[0][(int(page_num) * 10) - 10: (int(page_num) * 10)]
    cur_class = "ALL"
    cur_search = search_result[0]

    return render(request, 'index.html', { 'sentence' : search_sentence, 'search_result' : doc_list,
                                           'cluster_result' : search_result[1] , "page" : "1",
                                           "page_list" : page_list, "cur_class": "ALL"})


def make_doc_list(dtttu, result, seg_list):
    doc_dict = {}
    for elem in dtttu:
        doc_dict[elem['doc_id']] = elem

    search_result = []
    for doc_id in result[0]:
        doc_id = int(doc_id)
        title_label = doc_dict[doc_id]['title']
        time_label = ""
        url_label = doc_dict[doc_id]['url']
        text_label = doc_dict[doc_id]['text'][len(title_label):]
        text_idx = len(title_label)

        check_title = text_label[0: len(title_label)]

        if check_title == title_label:
            text_label = text_label[len(title_label):]
            text_idx = text_idx + len(title_label)

        # text 处理 <em>
        text_tuple_list = []
        min_index = 100000
        for elem in seg_list:
            if elem in settings.term_index_dict:
                index = settings.term_index_dict[elem]
                if str(doc_id) in settings.word_wij_invert_nk[index]['invert_index']:
                    for tup in settings.word_wij_invert_nk[index]['invert_index'][str(doc_id)]:
                        if tup[0] >= text_idx and tup[0] < min_index:
                            min_index = tup[0]

        if min_index == 100000:
            text_tuple_list = [(text_label[0: 100], "")]
        else:

            text_label = text_label[(min_index - text_idx): (min_index - text_idx) + 100]
            # print(doc_id)
            # print(min_index - text_idx)

            temp_list = []
            for elem in seg_list:
                if elem in settings.term_index_dict:
                    index = settings.term_index_dict[elem]
                    if str(doc_id) in settings.word_wij_invert_nk[index]['invert_index']:
                        for tup in settings.word_wij_invert_nk[index]['invert_index'][str(doc_id)]:
                            if tup[1] < min_index + 100 and tup[0] >= min_index:
                                temp_list.append((tup[0] - min_index, tup[1] - min_index))
            # print(temp_list)

            temp_boolean = ["0"] * 100
            for elem in temp_list:
                for i in range(elem[0], elem[1]):
                    temp_boolean[i] = "1"

            temp_boolean = ''.join(temp_boolean)
            # print(temp_boolean)
            # print(title_label)
            cur_elem = 0
            idx = 0
            while (idx < 100):
                if cur_elem == 0:
                    new_idx = temp_boolean.find("1", idx)
                    if new_idx == -1:
                        text_tuple_list.append((text_label[idx:], ""))
                        break
                    else:
                        text_tuple_list.append((text_label[idx:new_idx], ""))
                        idx = new_idx
                        cur_elem = 1
                else:
                    new_idx = temp_boolean.find("0", idx)
                    if new_idx == -1:
                        text_tuple_list.append(("", text_label[idx:]))
                        break
                    else:
                        text_tuple_list.append(("", text_label[idx:new_idx]))
                        idx = new_idx
                        cur_elem = 0

            temp_list = []
            temp_tuple = ['', '']
            for elem in text_tuple_list:
                if elem[0] == "" and elem[1] != "":
                    if temp_tuple[0] == '':
                        temp_list.append(elem)
                    else:
                        temp_list.append((temp_tuple[0], elem[1]))
                        temp_tuple = ['', '']
                elif elem[0] != "" and elem[1] == "":
                    temp_tuple[0] = elem[0]
            if temp_tuple[0] != '':
                temp_list.append((temp_tuple[0], ''))

            text_tuple_list = temp_list
        text_tuple_list.append(("...", ""))
        # print(text_tuple_list)

        # url 和 text 只显示一部分
        if doc_dict[doc_id]['time'] != "None":
            time_label = doc_dict[doc_id]['time']
        if len(doc_dict[doc_id]['url']) > 50:
            url_label = url_label[0:50] + '...'
        # if len(doc_dict[doc_id]['text']) > 100:
        #    text_label = text_label[0:100] + '...'

        # title 处理 <em>

        temp_list = []
        for elem in seg_list:
            if elem in settings.term_index_dict:
                index = settings.term_index_dict[elem]
                # print(settings.word_wij_invert_nk[index]['title_invert_index'])
                # print(doc_id)
                if str(doc_id) in settings.word_wij_invert_nk[index]['title_invert_index']:
                    for tup in settings.word_wij_invert_nk[index]['title_invert_index'][str(doc_id)]:
                        temp_list.append((tup[0], tup[1]))

        temp_boolean = ["0"] * len(title_label)
        for elem in temp_list:
            for i in range(elem[0], elem[1]):
                temp_boolean[i] = "1"

        temp_boolean = ''.join(temp_boolean)
        # print(temp_boolean)
        # print(title_label)
        title_tuple_list = []
        cur_elem = 0
        idx = 0
        while (idx < len(title_label)):
            if cur_elem == 0:
                new_idx = temp_boolean.find("1", idx)
                if new_idx == -1:
                    title_tuple_list.append((title_label[idx:], ""))
                    break
                else:
                    title_tuple_list.append((title_label[idx:new_idx], ""))
                    idx = new_idx
                    cur_elem = 1
            else:
                new_idx = temp_boolean.find("0", idx)
                if new_idx == -1:
                    title_tuple_list.append(("", title_label[idx:]))
                    break
                else:
                    title_tuple_list.append(("", title_label[idx:new_idx]))
                    idx = new_idx
                    cur_elem = 0

        temp_list = []
        temp_tuple = ['', '']
        for elem in title_tuple_list:
            if elem[0] == "" and elem[1] != "":
                if temp_tuple[0] == '':
                    temp_list.append(elem)
                else:
                    temp_list.append((temp_tuple[0], elem[1]))
                    temp_tuple = ['', '']
            elif elem[0] != "" and elem[1] == "":
                temp_tuple[0] = elem[0]
        if temp_tuple[0] != '':
            temp_list.append((temp_tuple[0], ''))

        title_tuple_list = temp_list
        # print(title_tuple_list)

        search_result.append((title_tuple_list, time_label, text_tuple_list, doc_dict[doc_id]['url'], url_label, doc_id))

    cluster_result = [("ALL", len(search_result), result[0])]
    for elem in result[1]:
        key = "".join(list(elem.keys()))
        cluster_result.append((key, len(elem[key]), elem[key]))

    return (search_result, cluster_result)


def search_cluster(query_seg_list):
    # print (os.getcwd())  # 获取当前工作目录路径
    # print (os.path.abspath('.'))  # 获取当前工作目录路径
    file_list = os.listdir("preprocess/pachong/")
    doc_num = len(file_list)
    query_doc_sim_dict = {}
    query_wij = [0] * len(settings.term_index_dict)

    tmp_list = []
    for word in query_seg_list:
        if word not in ['\n', ' ', '\t', ' ']:
            elem = settings.porter_stemmer.stem(word)
            if elem in settings.term_index_dict:
                index = settings.term_index_dict[elem]

                # 从invert_index获取文档列表
                for doc_name in settings.word_wij_invert_nk[index]['invert_index']:
                    query_doc_sim_dict[doc_name] = 0

                # 创建query的 单词-文档矩阵
                query_wij[index] = query_wij[index]  + 1
                # settings.word_wij_invert_nk[index]['wij'][0] = settings.word_wij_invert_nk[index]['wij'][0] + 1
                tmp_list.append(elem)

    if tmp_list == []:
        return ([], [])

    query_seg_list = tmp_list
    mq = 0
    for word in query_seg_list:  # 计算 mq
        elem = settings.porter_stemmer.stem(word)
        index = settings.term_index_dict[elem]
        if query_wij[index]  > mq:
            mq = query_wij[index]

    dq = 0
    for elem in settings.term_index_dict:  # 计算 Wkq , dq 然后计算 similarity
        index = settings.term_index_dict[elem]
        if query_wij[index] == 0:
            idf = math.log((doc_num / settings.word_wij_invert_nk[index]['nk']), 10) + 1
            wkq = idf / 2

            query_wij[index] = wkq
        else:
            tf = query_wij[index] / mq
            idf = math.log((doc_num / settings.word_wij_invert_nk[index]['nk']), 10) + 1
            wkq = tf * idf

            query_wij[index] = wkq

        for doc in query_doc_sim_dict:  # 计算 similarity 分子
            query_doc_sim_dict[doc] = query_doc_sim_dict[doc] + (
                settings.word_wij_invert_nk[index]['wij'][int(doc)] * query_wij[index])

        dq = dq + (query_wij[index] * query_wij[index])

    dq = dq ** 0.5  # 取根号

    for doc in query_doc_sim_dict:  # 计算 similarity
        query_doc_sim_dict[doc] = query_doc_sim_dict[doc] / (
            settings.doc_dj_keyword_weight_title_url_time_text[int(doc)]['dj'] * dq)

    doc_list = sorted(query_doc_sim_dict.items(), key=lambda x: x[1], reverse=True)

    search_result = []
    for elem in doc_list:
        search_result.append(elem[0])
    # print(search_result[0:100])

    classify_num = 100
    classify_list = doc_list[0:classify_num]
    classify_num = len(classify_list)

    # print(classify_list) # 相似度排序结果

    keys = []
    classify_dict = {}  # 关键词 - 文档编号
    doc_vector_dict = {}  # 文档编号 - 关键词 wij

    # 用搜索结果的关键词，建立新的文档-关键词矩阵
    for idx in range(0, classify_num):
        keys = keys + settings.doc_dj_keyword_weight_title_url_time_text[int(classify_list[idx][0])]['keywords']
        for word in settings.doc_dj_keyword_weight_title_url_time_text[int(classify_list[idx][0])]['keywords']:
            if word not in ['\n', ' ', '\t', ' ']:
                index = settings.term_index_dict[word]
                if word in classify_dict:
                    classify_dict[word][idx] = settings.word_wij_invert_nk[index]['wij'][int(classify_list[idx][0])]
                else:
                    classify_dict[word] = [0] * classify_num
                    classify_dict[word][idx] = settings.word_wij_invert_nk[index]['wij'][int(classify_list[idx][0])]
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
            center_distance_dict[doc_id] = center_distance_dict[doc_id] + (doc_vector_dict[doc_id][idx] - center_vector[
                idx]) ** 2

    for doc_id in doc_vector_dict:
        center_distance_dict[doc_id] = center_distance_dict[doc_id] ** (0.5)
        # print(center_distance_dict[doc_id])

    # print('创建每个文档的索引字典')
    doc_matrix_index = {}
    index = 0
    for elem in doc_vector_dict:
        doc_matrix_index[elem] = index
        index = index + 1

    # print('计算每个文档之间的最短距离')
    doc_dist_matrix = [0] * classify_num
    doc_dist_matrix = [doc_dist_matrix] * classify_num
    distance_check = [0] * (classify_num * classify_num)
    stop_doc = []
    count = 0
    for x in doc_vector_dict:
        stop_doc.append(x)
        for y in doc_vector_dict:
            if y not in stop_doc:
                for idx in range(0, keys_nbr):
                    distance_check[count] = distance_check[count] + (doc_vector_dict[x][idx] - doc_vector_dict[y][
                        idx]) ** 2
                distance_check[count] = distance_check[count] ** (0.5)

                id1 = doc_matrix_index[x]
                id2 = doc_matrix_index[y]
                doc_dist_matrix[id1][id2] = distance_check[count]
                doc_dist_matrix[id2][id1] = distance_check[count]

                count = count + 1

    distance_check = distance_check[0:count]

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

    # 重心点聚类
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

    # 节点之间聚类
    if (min_dist + 2) < classify_distance:
        classify_distance = (min_dist + 2)
    # print('classify_distance: '+ str(classify_distance))

    while (len(class_verify_list) != 0):
        cur_doc = class_verify_list[0]
        cur_vector = doc_vector_dict[cur_doc]
        min_distance = 10000
        min_node = ''
        for id in doc_vector_dict:
            temp_distance = 0
            if id != cur_doc:
                if ',' in id:
                    for idx in range(0, keys_nbr):
                        temp_distance = temp_distance + (doc_vector_dict[id][idx] - cur_vector[idx]) ** 2
                    temp_distance = temp_distance ** (0.5)
                    # print(temp_distance)

                    if temp_distance < min_distance:
                        min_distance = temp_distance
                        min_node = id
                else:
                    x = doc_matrix_index[cur_doc]
                    y = doc_matrix_index[id]
                    temp_distance = doc_dist_matrix[x][y]
                    if temp_distance < min_distance:
                        min_distance = temp_distance
                        min_node = id

        class_verify_list.remove(cur_doc)

        if min_distance >= (classify_distance):  # TODO
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

    # print(class_list)

    # 做以关键词为key，以文档列表为value的聚类字典
    for doc_id in class_list:
        if ',' in doc_id:
            temp_list = doc_id.split(',')
            temp_dict = {}
            for id in temp_list:
                key_list = settings.doc_dj_keyword_weight_title_url_time_text[int(id)]['keyword_weight']
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
            keyword = settings.doc_dj_keyword_weight_title_url_time_text[int(doc_id)]['keyword_weight'][0][0]
            if keyword in class_word:
                class_word[keyword].append(doc_id)
            else:
                class_word[keyword] = [doc_id]

    # 按文档列表长度排序聚类结果
    cluster_result = []
    check_duplication = []
    temp_list = []
    for word in class_word:
        if len(class_word[word]) > 1:
            cluster_result.append({word: class_word[word]})
            check_duplication.append(word)
        else:
            temp_list.append({word: class_word[word]})

    if len(cluster_result) <= 10:
        for elem in query_seg_list:
            if elem in class_word and elem not in check_duplication:
                cluster_result.append({elem: class_word[elem]})

        if len(cluster_result) <= 10:
            cluster_result = cluster_result + temp_list

    max_len = 0
    for elem in cluster_result:
        elem_len = len(elem[list(elem.keys())[0]])
        if elem_len > max_len:
            max_len = elem_len

    temp_list = []
    while (max_len > 0):
        for elem in cluster_result:
            if len(elem[list(elem.keys())[0]]) == max_len:
                temp_list.append(elem)
        max_len = max_len - 1

    if len(temp_list) > 10:
        cluster_result = temp_list[0:10]
    else:
        cluster_result = temp_list

    return (search_result, cluster_result)