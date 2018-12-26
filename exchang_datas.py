# -*- coding: utf8 -*-
# 获取交易所数据

import ccxt.async as ccx
okcoin = ccxt.async.okcoin ()
markets = okcoin.load_markets ()
print (markets)