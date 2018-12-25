# -*- coding: utf8 -*-
# 获取交易所数据

import ccxt
hitbtc = ccxt.hitbtc({'verbose': True})
hitbtc_markets = hitbtc.load_markets()
print(hitbtc.id, hitbtc_markets)