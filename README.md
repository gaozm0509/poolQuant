

- 程序说明
    - 列出nicehash上所有的算法
    - 通过列出的算法找到对应的coin和矿池
    - 根据当前全网难度和矿池费率计算收益（币的数量，单位数量）
    - 在市场上换算成比特币，计算最优组合（算法，币，矿池，市场）
    整体流程：在 nicehash 通过 btc 买入算力挖币，挖到币后卖出得到的 btc 数量如果大于买入算力时所用 btc 的数量，这生意就能做

- 文件说明
    - feixiaohao_datas 从非小号网站爬取市值前500的虚拟货币并存储到数据库(coins_info)
    - coins_from_algorithm 指定算法返回该算法所用的虚拟货币，如果不传入算法名
       返回，所有算法和所有算法对应的虚拟货币，并存入数据库（coin_algorithm）
    - get_algorithm 获取 nicehash 上已经用到的算法，和算法对应的价格，存入数据库（algorithms_info）
    - pool_quant_main






