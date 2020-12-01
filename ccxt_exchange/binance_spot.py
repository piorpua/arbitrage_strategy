from ccxt.async_support import binance


# 币安现货
class binance_spot (binance):

    def describe(self):
        super_describe = super().describe()
        super_describe['options']['defaultType'] = 'spot'

        return super_describe
