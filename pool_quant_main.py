# -*- coding: utf8 -*-
# 主文件

from pymongo import MongoClient
import exchang_datas

#获取非小号数据
# coins_info = db['coins_info']
# coins_info_datas = coins_info['data']


# 获取nicehash中的算力信息
# 计算结果
def get_reulst():
    db_client = MongoClient('mongodb://127.0.0.1:27017/')
    db = db_client['PoolQuant']

    #从数据库中获取需要计算的币种信息
    coin_algorithm_col = db['coin_algorithm']
    coin_algorithm = coin_algorithm_col.find_one()
    coin_dic = coin_algorithm['coins']
    #获取指定的几个交易所包含的币种
    market_infos = db['market_infos']
    market_coins = market_infos.find_one()

    algorithms_info_col = db['algorithms_info']
    algorithms_info = algorithms_info_col.find_one()

    # nicehash 算力挖矿单位
    algorithm_unit_col = db['algorithm_unit']
    algorithm_unit = algorithm_unit_col.find_one()
    algorithm_unit_info = algorithm_unit['algorithm']
    coins = []
    for key in coin_dic.keys():
        coins.extend(coin_dic[key])
    print('目标币种',coins,'\n')
    for index,coin in enumerate(coins):
        # 计算交易所该币的价格
        current_price_btc = 0
        coin_short_name = coin['coin_short_name']
        print(index,'币种：',coin_short_name)
        if coin_short_name == 'BTC':
            continue
        okex = exchang_datas.OKEX
        huobi = exchang_datas.HUOBI
        bina = exchang_datas.BIN
        plx = exchang_datas.PLX
        cry = exchang_datas.CRY
        bix = exchang_datas.BIX
        min_exchange = '指定交易所没有该币种'
        for ok_coins in market_coins[okex]:
            if coin_short_name in ok_coins:
                current_price_btc = exchang_datas.get_price_from_key(
                    ok_coins, okex)
                # print('=====', current_price_btc)
                break

        for huobi_coins in market_coins[huobi]: 
            if coin_short_name in huobi_coins:
                price_btc = exchang_datas.get_price_from_key(
                    huobi_coins, huobi)
                if current_price_btc > price_btc:
                    current_price_btc = price_btc
                    min_exchange = huobi

        for bina_coins in market_coins[bina]:
            if coin_short_name in bina_coins:
                price_btc = exchang_datas.get_price_from_key(bina_coins, bina)
                if current_price_btc > price_btc:
                    current_price_btc = price_btc
                    min_exchange = bina

        for plx_coins in market_coins[plx]:
            if coin_short_name in plx_coins:
                price_btc = exchang_datas.get_price_from_key(plx_coins, plx)
                if current_price_btc > price_btc:
                    current_price_btc = price_btc
                    min_exchange = plx

        # for cry_coins in market_coins[cry]:
        #     if coin_short_name in cry_coins:
        #         price_btc = exchang_datas.get_price_from_key(cry_coins, cry)
        #         if current_price_btc > price_btc:
        #             current_price_btc = price_btc
        #             min_exchange = cry

        for bix_coins in market_coins[bix]:
            if coin_short_name in bix_coins:
                price_btc = exchang_datas.get_price_from_key(bix_coins, bix)
                if current_price_btc > price_btc:
                    current_price_btc = price_btc
                    min_exchange = bix

        key = coin['algorithm']
        print('交易市场最低价：', current_price_btc, '/', min_exchange)

        print('所有目标币种算法：',algorithms_info.keys())
        # 获取挖矿价格
        if key in algorithms_info.keys():
            algorithms_dic = algorithms_info[key]
            algorithm_price = algorithms_dic['price']
            if 'estimated_reward' in coin.keys():
                estimated_reward = coin['estimated_reward']
                hashrate_unit = coin['hashrate_unit']
                unit_key = key.lower()
                nice_hash_unit = algorithm_unit_info[unit_key]['suffix']
                algorithm_price_btc = float(estimated_reward) * float(
                    algorithm_price)

                print('算力市场价格：', algorithm_price_btc, 'niceHashUnit:',
                      nice_hash_unit, 'crptoUnit:', hashrate_unit, '\n')
        else:
            print('市场最低价：coin["algorithm"]未找到')


get_reulst()