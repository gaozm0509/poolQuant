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
    print('所有交易所：',market_coins)
    algorithms_info_col = db['algorithms_info']
    algorithms_info = algorithms_info_col.find_one()

    # nicehash 算力挖矿单位
    algorithm_unit_col = db['algorithm_unit']
    algorithm_unit = algorithm_unit_col.find_one()
    algorithm_unit_info = algorithm_unit['algorithm']
    coins = []
    for key in coin_dic.keys():
        coins.extend(coin_dic[key])
    # print('目标币种',coins,'\n')
    for index,coin in enumerate(coins):
        # 计算交易所该币的价格
        current_price_btc = 0.0
        coin_short_name = coin['coin_short_name']
        if coin_short_name == 'BTC':
            continue
        print(index,coin_short_name,":")
        okex = exchang_datas.OKEX
        huobi = exchang_datas.HUOBI
        bina = exchang_datas.BIN
        plx = exchang_datas.PLX
        cry = exchang_datas.CRY
        bix = exchang_datas.BIX
        max_exchange = '指定交易所没有该币种'

        transaction_pair = coin_short_name + '/BTC'
        for ok_coins in market_coins[okex]:
            if transaction_pair in ok_coins:
                current_price_btc = exchang_datas.get_price_from_key(
                    ok_coins, okex)
                print(okex,'价格：',current_price_btc)
                max_exchange = okex
                break

        for huobi_coins in market_coins[huobi]: 
            if transaction_pair in huobi_coins:
                price_btc = exchang_datas.get_price_from_key(
                    huobi_coins, huobi)
                print(huobi,'价格：',price_btc)
                if current_price_btc <= price_btc:
                    current_price_btc = price_btc
                    max_exchange = huobi
                    break

        for bina_coins in market_coins[bina]:
            if transaction_pair in bina_coins:
                price_btc = exchang_datas.get_price_from_key(bina_coins, bina)
                print(bina,'价格：',price_btc)
                if current_price_btc <= price_btc:
                    current_price_btc = price_btc
                    max_exchange = bina
                    break

        for plx_coins in market_coins[plx]:
            if transaction_pair in plx_coins:
                price_btc = exchang_datas.get_price_from_key(plx_coins, plx)
                print(plx,'价格：',price_btc)
                if current_price_btc <= price_btc:
                    current_price_btc = price_btc
                    max_exchange = plx
                    break

        # for cry_coins in market_coins[cry]:
        #     if coin_short_name in cry_coins:
        #         price_btc = exchang_datas.get_price_from_key(cry_coins, cry)
        #         if current_price_btc > price_btc:
        #             current_price_btc = price_btc
        #             min_exchange = cry

        for bix_coins in market_coins[bix]:
            if transaction_pair in bix_coins:
                price_btc = exchang_datas.get_price_from_key(bix_coins, bix)
                print(bix,'价格：',price_btc)
                if current_price_btc <= price_btc:
                    current_price_btc = price_btc
                    max_exchange = bix
                    break

        key = coin['algorithm']
        print('交易市场最高价：', current_price_btc, '/', max_exchange)

        # print('所有目标币种算法：',algorithms_info.keys())
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

                print('挖矿成本：', algorithm_price_btc, 'niceHashUnit:',
                      nice_hash_unit, 'crptoUnit:', hashrate_unit, '\n')
        else:
            print('挖矿成本：coin["algorithm"]未找到')


get_reulst()