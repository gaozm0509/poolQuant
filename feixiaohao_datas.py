# -*- coding: utf8 -*-
# 爬取非小号上的数据

import requests
import time
from bs4 import BeautifulSoup
from pymongo import MongoClient
import json


def get_datas():
    url = 'https://dncapi.feixiaohao.com/api/coin/coinrank?page=1&type=0&pagesize=500&webp=1'
    r = requests.get(url)
    dic = eval(r.text)
    dic['update_condition'] = 1
    db_client = MongoClient('mongodb://127.0.0.1:27017/')
    db = db_client['PoolQuant']
    col = db['coins_info']
    condition = {'update_condition': 1}
    db_dic = col.find_one(condition)
    if db_dic:
        # 更新
        db_dic['data'] = dic['data']
        col.update_one(condition, {'$set': db_dic})
    else:
        # 插入
        col.insert_one(dic)


def get_exchange_datas():
    url = 'https://dncapi.feixiaohao.com/api/exchange/coinpair_list'
    # bittrex
    post_data = {
        'code': "bittrex",
        'page': 1,
        'pagesize': 1000,
        'token': "",
        'webp': 1,
    }
    headers = {
        'Accept':
        'application/json, text/plain */*',
        'Accept-Encoding':
        'gzip, deflate, br',
        'Accept-Language':
        'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection':
        'keep-alive',
        'Content-Length':
        '63',
        'Content-Type':
        'application/json;charset=UTF-8',
        'Host':
        'dncapi.feixiaohao.com',
        'Origin':
        'https://www.feixiaohao.com',
        'Referer':
        'https://www.feixiaohao.com/exchange/bittrex/',
        'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
    }
    r = requests.post(url, post_data, headers=headers)
    print(r.text)


get_exchange_datas()