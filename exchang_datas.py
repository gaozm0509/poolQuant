# -*- coding: utf8 -*-
# 获取交易所数据

import ccxt
from pymongo import MongoClient

OKEX = 'okex'
HUOBI = 'huobi'
CRY = 'cryptopia'
BIN = 'Binance'
BIX = 'Bittrex'
PLX = 'Poloniex'

MK_LIST = [OKEX, HUOBI, CRY, BIN, BIX, PLX]


def get_market_info(market=OKEX):
    """ 抓取交易所交易对，并跟新到数据库 """
    mk = get_market(market)
    markets = mk.load_markets()
    l = [i for i in markets.keys() if '/BTC' in i]
    db_client = MongoClient('mongodb://127.0.0.1:27017/')
    db = db_client['PoolQuant']
    db_col = db['market_infos']
    condition = {'update_condition': 1}
    db_dic = db_col.find_one(condition)

    if db_dic:
        # 更新
        db_dic[market] = l
        db_col.update_one(condition, {'$set': db_dic})
        print('更新', market, '完成')
    else:
        # 插入
        dic = {'update_condition': 1, market: l}
        db_col.insert_one(dic)
        print('插入', market, '完成')


def get_market(market=OKEX):
    mk = ccxt.okcoinusd()
    if market == HUOBI:
        mk = ccxt.huobipro()
    if market == CRY:
        mk = ccxt.cryptopia()
    if market == BIN:
        mk = ccxt.binance()
    if market == PLX:
        mk = ccxt.poloniex()
    return mk


def get_price_from_key(key, market=OKEX):
    """ 从指定交易所（mk）获取指定交易对（key）的价格 """
    # 实例化市场
    exchange = get_market(market)
    # 获取ticker信息
    ticker = exchange.fetch_ticker(key)
    print(ticker)
    if 'ask' in ticker.keys():
        return ticker['ask']
    if 'info' in ticker.keys():
        return ticker['info']['AskPrice']


def run():
    for mk in MK_LIST:
        get_market_info(mk)

