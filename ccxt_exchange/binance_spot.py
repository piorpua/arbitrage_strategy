from ccxt_exchange.binance_base import binance_base


# 币安现货
class binance_spot (binance_base):

    def describe(self):
        super_describe = super().describe()
        super_describe['options']['defaultType'] = 'spot'

        return super_describe
