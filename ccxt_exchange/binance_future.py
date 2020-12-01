from ccxt.async_support import binance


# 币安 USDT 永续合约
class binance_future (binance):

    def describe(self):
        super_describe = super().describe()
        super_describe['options']['defaultType'] = 'future'

        return super_describe
