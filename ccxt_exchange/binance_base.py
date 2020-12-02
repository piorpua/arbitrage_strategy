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

    async def fetch_funding_rate_history(self, symbol, since=None, limit=None, params=None):
        params = params or {}

        await self.load_markets()
        market = self.market(symbol)
        request = {
            'symbol': market['id'],
        }

        if since is not None:
            request['startTime'] = since

        if limit is not None:
            request['limit'] = min(limit, 1000)

        defaultType = self.safe_string_2(self.options, 'fetchBidsAsks', 'defaultType', 'spot')
        type = self.safe_string(params, 'type', defaultType)

        query = self.omit(params, 'type')
        if type == 'future':
            method = 'fapiPublicGetFundingRate'
        elif type == 'delivery':
            method = 'dapiPublicGetFundingRate'
        else:
            raise ExchangeError(self.id + " does not support '" + type + "' type, set exchange.options['defaultType'] to 'spot', 'margin', 'delivery' or 'future'")
        response = await getattr(self, method)(self.extend(request, query))
        # {
        #     "symbol": "BTCUSDT",
        #     "fundingTime": 1606896000011,
        #     "fundingRate": "0.00010000"
        # }
        result = []
        for funding_rate_info in response:
            result.append({
                'info': funding_rate_info,
                'fundingTime': self.safe_integer(funding_rate_info, 'fundingTime'),
                'fundingRate': self.safe_float(funding_rate_info, 'fundingRate')
            })
        return result
