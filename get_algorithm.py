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
        orders = [l for l in orders if int(l[5]) > 200]
        # 按照 price 排序
        orders.sort(key=operator.itemgetter(3), reverse=False)
        # 去最优
        order = orders[0]
        order_dic = {}
        order_dic['order'] = order[0]  # 订单号
        order_dic['price'] = order[3]  # 价格，单价
        order_dic['limit'] = order[4]  # 不知道
        order_dic['miners'] = order[5]  # 旷工数
        order_dic['speed'] = order[6]  # 速度
        all_dic[algorithm] = order_dic

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



def get_unit(algorithms=None):
    """ 更新nicehash算法对应的算力计量单位 """
    if algorithms is None:
        algorithms = get_algorithm_list()
    unit_url = 'https://www.nicehash.com/marketplace/scrypt'
    unit_r = requests.get(unit_url)
    unit_text = str(unit_r.text)
    begin_index = unit_text.find('ALGORITHMS:')
    end_index = unit_text.index('SERVERS:')
    unit_text = unit_text[begin_index:end_index]
    unit_text = unit_text.strip()
    unit_text = unit_text[len('ALGORITHMS:'):-1] # 去掉逗号
    unit_dic = eval(unit_text)

    # 跟新到数据库
    db_col = db['algorithm_unit']
    algorithm_unit = db_col.find_one()
    condition = {'update_condition': 1}
    if algorithm_unit:
        # 更新
        db_col.update_one(condition, {'$set': unit_dic})
    else:
        # 插入
        db_col.insert_one({'update_condition':1,'algorithm':unit_dic})
    print(unit_dic)
        


def get_algorithm_list():
    """ 获取算力名称列表 """
    algorithms = db['algorithms']
    return algorithms.find_one()['datas']


get_unit()
algorithm_info()

