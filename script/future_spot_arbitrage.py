import asyncio
import functools
import logging as system_logging

import simplejson as json

from ccxt_exchange.binance_future import binance_future
from common.logging_custom import logging_custom_instance

logging_custom_instance.initialize(level=system_logging.INFO)
logging = logging_custom_instance.get_logging()


async def parse_response_decimal(func, *args):
    try:
        result = await func(*args)
    except Exception as e:
        raise e
    return json.loads(json.dumps(result), use_decimal=True)


async def funding_rate_info():

    def __inner_compare(_left, _right):
        funding_rate_compare = 0
        if _left['lastFundingRate'] > _right['lastFundingRate']:
            funding_rate_compare = -1
        elif _left['lastFundingRate'] < _right['lastFundingRate']:
            funding_rate_compare = 1
        if funding_rate_compare != 0:
            return funding_rate_compare
        return 1 if _left['info']['symbol'] > _right['info']['symbol'] else -1

    future_client = binance_future()
    try:
        funding_rate_list = await parse_response_decimal(future_client.fetch_funding_rate)
        funding_rate_list = sorted(funding_rate_list, key=functools.cmp_to_key(__inner_compare))
        for funding_rate in funding_rate_list:
            logging.info(f"{funding_rate['info']}")
    finally:
        await future_client.close()


async def funding_rate_history():
    pass


async def main():
    await funding_rate_info()


if '__main__' == __name__:
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(main())
