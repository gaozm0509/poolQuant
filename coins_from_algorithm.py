# -*- coding: utf8 -*-
# 在 https://www.crypto-coinz.net/coins-calculator/ 中寻找算法对应的币种

import requests
import time
from bs4 import BeautifulSoup
from pymongo import MongoClient

update_day = 10  #数据库更新间隔时间


def getCoins(algorithm_key=None):
    """ 通过算力名称(algorithm_key)获取算力对应的 coins """
    # 先从数据库获取资源,如果资源存在则直接获取数据库资源
    curr_time = int(time.time())
    db_client = MongoClient('mongodb://127.0.0.1:27017/')
    db = db_client['PoolQuant']
    col = db['coin_algorithm']
    col_reuslt = col.find_one()
    if col_reuslt:
        db_time = int(col_reuslt['time'])
        # 从输入库获取数据
        if curr_time - db_time < update_day * 24 * 60 * 60:
            result = col_reuslt['coins']
            single_result = []
            # 如果传入 algorithm_key
            if algorithm_key:
                for item in result:
                    if algorithm_key == item[0]['algorithm']:
                        single_result = item
                        result = single_result
                        break
            return result

    url = 'https://www.crypto-coinz.net/coins-calculator/'
    r = requests.get(url)
    bs = BeautifulSoup(r.text, features='html.parser')
    texts = bs.find_all('div', class_='coin')
    l = []
    for coin_div in texts:
        item_bs = BeautifulSoup(str(coin_div), features='html.parser')
        # 算法名称
        al = str(item_bs.find_all('font'))
        font = '<font style="color: green">'
        al = al[len(font) + 1:-1]
        al = al[:-7]

        # 币名称
        coin_name = str(item_bs.find_all('a'))
        first_index = coin_name.find('<br/>')
        coin_name = coin_name[first_index + 5:-1]
        last_index = coin_name.find('<br/>')
        coin_name = coin_name[:last_index]

        # 币简称
        name_l = coin_name.split(' ')
        coin_all_name = name_l[0]
        coin_short_name = name_l[-1]
        coin_short_name = coin_short_name[1:]
        coin_short_name = coin_short_name[:-1]

        # 算力和币的关系
        a_tab = (item_bs.find('a'))
        a_tab_str = str(a_tab.get('href'))
        a_key = a_tab_str[11:-11]
        key_url = 'https://www.crypto-coinz.net/coin-info/' + a_key + 'calculator/'
        key_post_params = {
            'what_to_calculate': 1,
            'power': 0,
            'hardwareCost': 0,
            'electricityCost': 0,
            'poolFee': 0,
            'chooseExchange': 1,
            'submit_data': 'Calculate'
        }
        key_r = requests.post(key_url, key_post_params)
        key_bs = BeautifulSoup(key_r.text, features='html.parser')
        table = key_bs.find('table', id='tblmd')
        # 如果没有需要的数据，则下一个循环
        if table is None:
            print(coin_name,'-table 抓取失败',)
            continue
        trs = table.find_all('tr', id='row')
        # 如果没有需要的数据，则下一个循环
        if len(trs) < 3:
            print(coin_name,'tr id=row 抓取失败',)
            continue
        day_tr = trs[2]
        tds = day_tr.find_all('td')
        td_dic = {}
        for index, td in enumerate(day_tr):
            if index == 1:
                td_dic['estimated_reward'] = str(td.text)
            if index == 2:
                td_dic['exchange_rate'] = str(td.text).replace(' ', '')

        
        # 获取单位
        unit_bs = BeautifulSoup(key_r.text,features='html.parser')
        unit_divs = unit_bs.find_all('div',class_ = 'input-group input-group-sm input-group-1st')
        unit_div = unit_divs[0]
        unit = str(unit_div.find('div',class_ = 'input-group-append-coin').text)

        # 数据放入集合
        dic = td_dic
        dic['algorithm'] = al
        dic['coin_all_name'] = coin_all_name
        dic['coin_short_name'] = coin_short_name
        dic['hashrate_unit'] = unit
        print(td_dic,'\n')
        l.append(dic)
        l.sort(key=lambda e: e.__getitem__('algorithm'))

    # 根据算法分组，得到
    # [
    #   [{'algorithm':'算法1','coin_all_name':'coin全名','coin_short_name':'coin简称',pool_url:'矿池列表'}],
    #   [{'algorithm':'算法2','coin_all_name':'coin全名','coin_short_name':'coin简称',pool_url:'矿池列表'}]
    # ]
    # 的list
    result = []
    for index, item in enumerate(l):
        if index == 0:
            result_item = []
            result_item.append(item)
            result.append(result_item)
        else:
            last_item = result[-1]
            if last_item[0]['algorithm'] == item['algorithm']:
                last_item.append(item)
            else:
                result_item = []
                result_item.append(item)
                result.append(result_item)
    # 插入数据库
    insert_dic = {'time': curr_time, 'coins': result, 'update_condition': 1}
    if col_reuslt:
        col.update_one({'update_condition': 1}, {'$set': insert_dic})
    else:
        col.insert_one(insert_dic)

    single_result = []
    # 如果传入 algorithm_key
    if algorithm_key:
        for item in result:
            if algorithm_key == item[0]['algorithm']:
                single_result = item
                result = single_result
                break
    return result


getCoins()

# # 矿池 list 链接
#         a_tab = (item_bs.find('a'))
#         a_tab_str = str(a_tab.get('href'))
#         a_key = a_tab_str[11:-11]
#         pool_urls = 'https://www.crypto-coinz.net/recommended-crypto-pools-for/' + a_key + 'mining-pools/'
#         # pool_urls = 'https://www.crypto-coinz.net/recommended-crypto-pools-for/?186-Dogecoin-DOGE-Scrypt-mining-pools/'
#         # 根据规则获取最优的矿池
#         print(pool_urls)
#         pool_r = requests.get(pool_urls)
#         pool_bs = BeautifulSoup(pool_r.text, features='html.parser')
#         pool_texts = pool_bs.find_all('tr',id = 'row')
#         # 如果没有矿池支持（pool_texts长度为0）则直接寻找下一条
#         if len(pool_texts) == 0:
#             continue
#         pool_list = []
#         for pool_text in pool_texts:
#             td_dic = {}
#             for index, td in enumerate(pool_text.find_all('td')):
#                 if index == 1:
#                     td_dic['pool_link'] = td.find('a')['href']
#                 if index == 2:
#                     s = str(td.text)
#                     s = s.replace(' ','')
#                     s = s.replace('\t','')
#                     s = s.replace('\n','')
#                     s = s.replace('%','')
#                     td_dic['commision'] = s
#                 if index == 3:
#                     s = str(td.text)
#                     s = s.replace(' ','')
#                     s = s.replace('\t','')
#                     s = s.replace('\n','')
#                     td_dic['workers'] = int(s)
#             pool_list.append(td_dic)
#         # 删选 pool_list
#         new_pool_list = [item for item in pool_list if item['workers'] >= 200]

#         # 如果没有矿池支持（pool_texts长度为0）则直接寻找下一条
#         if len(pool_texts) == 0:
#             continue

#         new_pool_list.sort(key=lambda e: e.__getitem__('commision'))
#         # if len(new_pool_list) > 3:
#         #     new_pool_list = new_pool_list[:3]