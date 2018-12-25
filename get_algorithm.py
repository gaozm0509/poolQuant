# -*- coding: utf8 -*-
# 获取 nicehash 算力价格
import requests
import time
import json
import re
import operator
from bs4 import BeautifulSoup
from pymongo import MongoClient

db_client = MongoClient('mongodb://127.0.0.1:27017/')
db = db_client['PoolQuant']


def algorithm_info(algorithms=None):
    """ 更新nicehash网页内容到数据库 """
    if algorithms is None:
        algorithms = get_algorithm_list()
    all_dic = {}
    for index, algorithm in enumerate(algorithms):
        url = 'https://api.nicehash.com/livePubJSON?l=0&a' + str(
            index) + '&a=0&callback=superagentCallback'
        # url = 'https://api.nicehash.com/livePubJSON?l=0&a=0&callback=superagentCallback'
        millis = str(int(round(time.time() * 1000)))
        url = url + millis

        keyword = 'superagentCallback' + millis
        r = requests.get(url)
        reslutStr = r.text[len(keyword):-1]
        reslutStr = reslutStr[1:-2]
        reslutStr = reslutStr.replace('\'', '\"')
        reslutStr = reslutStr.replace('..L', '')
        reslutStr = re.sub("u'", "\"", reslutStr)
        jsonReslut = None
        try:
            jsonReslut = json.loads(reslutStr)
        except json.decoder.JSONDecodeError:
            reslutStr = reslutStr + '}'
            jsonReslut = json.loads(reslutStr)

        # 删除旷工为零的元素
        orders = jsonReslut['usa']['orders']
        orders = [l for l in orders if int(l[5]) > 0]
        # 按照 price 排序
        orders.sort(key=operator.itemgetter(3), reverse=False)

        # orders 中的数组转成 dic
        order_dics = []
        for order in orders:
            order_dic = {}
            order_dic['order'] = order[0]  # 订单号
            order_dic['price'] = order[3]  # 价格，单价
            order_dic['limit'] = order[4]  # 不知道
            order_dic['miners'] = order[5]  # 旷工数
            order_dic['speed'] = order[6]  # 速度
            order_dics.append(order_dic)
        all_dic[algorithm] = order_dics

        ## 第一条插入更新 condition
        if index == 0:
            all_dic['update_condition'] = 1

        algorithms_info_col = db['algorithms_info']
        algorithms_info = algorithms_info_col.find_one()
        condition = {'update_condition': 1}
        if algorithms_info:
            # 更新
            algorithms_info_col.update_one(condition, {'$set': all_dic})
        else:
            # 插入
            algorithms_info_col.insert_one(all_dic)
        print('got', algorithm, '...')

    ### 为了时效性，把插入操作写到循环体中了

    # all_dic['update_condition'] = 1
    # algorithms_info_col = db['algorithms_info']
    # algorithms_info = algorithms_info_col.find_one()
    # condition = {'update_condition': 1}
    # if algorithms_info:
    #     # 更新
    #     algorithms_info_col.update_one(condition, {'$set': all_dic})
    # else:
    #     # 插入
    #     algorithms_info_col.insert_one(all_dic)


def get_unit(algorithms=None):
    """ 更新nicehash算法对应的算力计量单位 """
    if algorithms is None:
        algorithms = get_algorithm_list()
    all_dic = {}
    for index, algorithm in enumerate(algorithms):
        # 获取算力单位
        unit_url = 'https://www.nicehash.com/marketplace/' +  algorithm.lower()
        unit_r = requests.get(unit_url)
        unit_texts = BeautifulSoup(unit_r.text, features='html.parser')
        unit_trs = unit_texts.find_all('eu', class_='eu')
        # unit_tr = unit_trs[0]
        # unit = str(unit_tr.find('small').text)
        print(unit_url)


def get_algorithm_list():
    """ 获取算力名称列表 """
    algorithms = db['algorithms']
    return algorithms.find_one()['datas']


get_unit()
