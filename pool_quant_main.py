# -*- coding: utf8 -*-
# 主文件

from pymongo import MongoClient 


db_client = MongoClient('mongodb://127.0.0.1:27017/')
db = db_client['PoolQuant']

#从数据库中获取需要计算的币种信息
coin_algorithm_col = db['coin_algorithm']
coins = coin_algorithm_col['coins']

#获取非小号数据
coins_info = db['coins_info']
coins_info_datas = coins_info['data']

# 获取nicehash中的算力信息
for coin in coins:

    # 计算交易所该币的价格
    current_price_usd = 0
    for coins_info_data in coins_info_datas:
        if coin['coin_short_name'] == coins_info_data['name']:
            current_price_usd = coins_info_data['current_price_usd']
            break
    
    # 获取挖矿价格
    

