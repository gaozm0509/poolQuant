# -*- coding: utf8 -*-
# 获取交易所数据

import ccxt
okcoin = ccxt.okcoinusd ()
markets = okcoin.load_markets ()
print (okcoin.id, markets)