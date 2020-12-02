import asyncio
import logging as system_logging
import time
from decimal import Decimal

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


async def show_funding_rate_history(interval_days):
    one_day_millis = 24 * 60 * 60 * 1000
    interval_map = {
        '7D': 7 * one_day_millis,
        '30D': 30 * one_day_millis,
        '60D': 60 * one_day_millis,
        '90D': 90 * one_day_millis,
    }
    assert interval_days in interval_map, f'interval days only supported: {list(interval_map.keys())}'
    interval_millis = interval_map[interval_days]

    current_millis = int(time.time() * 1000)
    start_millis = current_millis - interval_millis

    future_client = binance_future()
    try:
        latest_funding_rate_dict = {}

        funding_rate_list = await parse_response_decimal(future_client.fetch_funding_rate)
        for funding_rate_info in funding_rate_list:
            latest_funding_rate_dict[funding_rate_info['info']['symbol']] = funding_rate_info['lastFundingRate']

        future_markets = await future_client.fetch_markets()

        funding_rate_list = []

        index = 0
        count = len(future_markets)
        for future_market in future_markets:
            symbol = future_market['symbol']

            logging.info(f'[{index + 1}/{count}] {symbol}')
            index += 1

            total_funding_rate = Decimal('0')
            funding_rate_count = 0

            since = start_millis
            while True:
                funding_rate_history = await parse_response_decimal(
                    future_client.fetch_funding_rate_history, symbol, since, 1000
                )
                funding_rate_history_count = len(funding_rate_history)
                if funding_rate_history_count <= 0:
                    break

                funding_rate_count += funding_rate_history_count
                for funding_rate_info in funding_rate_history:
                    total_funding_rate += funding_rate_info['fundingRate']

                since = funding_rate_history[-1]['fundingTime'] + 1

            average_funding_rate = total_funding_rate / funding_rate_count

            future_market_id = future_market['id']
            funding_rate_list.append({
                'symbol': future_market_id,
                'latestFundingRate': latest_funding_rate_dict.get(future_market_id),
                'avgFundingRate': average_funding_rate,
            })

            await asyncio.sleep(0.3)

        funding_rate_list = sorted(
            funding_rate_list, key=lambda item: (item['latestFundingRate'], item['avgFundingRate']), reverse=True
        )
        for funding_rate_info in funding_rate_list:
            logging.info(f'{json.dumps(funding_rate_info)}')
    finally:
        await future_client.close()


async def main():
    await show_funding_rate_history('90D')


if '__main__' == __name__:
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(main())
