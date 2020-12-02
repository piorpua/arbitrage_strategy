from ccxt.async_support import binance
from ccxt.base.errors import ExchangeError


class binance_base (binance):

    async def fetch_funding_rate(self, symbol=None, params=None):
        params = params or {}

        await self.load_markets()
        if symbol:
            market = self.market(symbol)
            request = {
                'symbol': market['id'],
            }
        else:
            request = {}

        defaultType = self.safe_string_2(self.options, 'fetchBidsAsks', 'defaultType', 'spot')
        type = self.safe_string(params, 'type', defaultType)

        query = self.omit(params, 'type')
        if type == 'future':
            method = 'fapiPublicGetPremiumIndex'
        elif type == 'delivery':
            method = 'dapiPublicGetPremiumIndex'
        else:
            raise ExchangeError(self.id + " does not support '" + type + "' type, set exchange.options['defaultType'] to 'spot', 'margin', 'delivery' or 'future'")
        response = await getattr(self, method)(self.extend(request, query))
        # {
        #     'symbol': 'BTCUSDT',
        #     'markPrice': '18897.57772886',
        #     'indexPrice': '18888.39464788',
        #     'lastFundingRate': '0.00010000',
        #     'interestRate': '0.00010000',
        #     'nextFundingTime': 1606896000000,
        #     'time': 1606894761000
        # }
        if symbol:
            response = [response]
        result = []
        for funding_rate_info in response:
            result.append({
                'info': funding_rate_info,
                'lastFundingRate': self.safe_float(funding_rate_info, 'lastFundingRate')
            })
        return result
