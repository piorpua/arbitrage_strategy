from ccxt_exchange.binance_base import binance_base


# 币安 USDT 永续合约
class binance_future (binance_base):

    def describe(self):
        super_describe = super().describe()
        super_describe['options']['defaultType'] = 'future'

        return super_describe
