# -*- coding: utf8 -*-
# 获取交易所数据

import ccxt
okex = ccxt.okex ()
# markets = okcoin.load_markets ()
symbol = 's/USDT'
ticker = okex.fetch_ticker(symbol)
print (ticker)