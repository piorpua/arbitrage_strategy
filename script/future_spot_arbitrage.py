import asyncio
import decimal
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


async def show_funding_rate_history():
    one_day_millis = 24 * 60 * 60 * 1000
    days_list = [7, 30, 60, 90, 180, 360]

    future_client = binance_future()
    try:
        latest_funding_rate_dict = {}

        latest_funding_rate_list = await parse_response_decimal(future_client.fetch_funding_rate)
        latest_funding_rate_list = sorted(
            latest_funding_rate_list, key=lambda item: item['lastFundingRate'], reverse=True
        )
        for funding_rate_info in latest_funding_rate_list:
            logging.info(f"{funding_rate_info['info']}")
            latest_funding_rate_dict[funding_rate_info['info']['symbol']] = funding_rate_info['lastFundingRate']

        future_markets = await future_client.fetch_markets()

        current_millis = int(time.time() * 1000)

        result = []

        index = 0
        count = len(future_markets)
        for future_market in future_markets:
            symbol = future_market['symbol']

            logging.info(f'[{index + 1}/{count}] {symbol}')
            index += 1

            funding_rate_history_list = []

            since = 0
            while True:
                funding_rate_history = await parse_response_decimal(
                    future_client.fetch_funding_rate_history, symbol, since, 1000
                )
                if len(funding_rate_history) <= 0:
                    break
                funding_rate_history_list.extend(funding_rate_history)

                since = funding_rate_history[-1]['fundingTime'] + 1

            interval_list = []
            for days in days_list:
                interval_list.append({
                    'days': days,
                    'interval_millis': days * one_day_millis,
                    'total': Decimal('0'),
                    'count': 0,
                })

            for funding_rate_info in funding_rate_history_list:
                fundingTime = funding_rate_info['fundingTime']
                fundingRate = funding_rate_info['fundingRate']

                for interval_info in interval_list:
                    if fundingTime > current_millis - interval_info['interval_millis']:
                        interval_info['total'] += fundingRate
                        interval_info['count'] += 1

            future_market_id = future_market['id']
            result_info = {
                'symbol': future_market_id,
                'latestFundingRate': latest_funding_rate_dict.get(future_market_id),
            }
            for interval_info in interval_list:
                days = interval_info['days']
                result_info[f'avgFundingRate_{days}D'] = (interval_info['total'] / interval_info['count']).quantize(
                    Decimal('10') ** Decimal('-8'), rounding=decimal.ROUND_DOWN
                )
            result.append(result_info)

            await asyncio.sleep(0.3)

        result = sorted(
            result, key=lambda item: item['latestFundingRate'], reverse=True
        )
        for funding_rate_info in result:
            logging.info(f'{json.dumps(funding_rate_info)}')
    finally:
        await future_client.close()


async def main():
    await show_funding_rate_history()


if '__main__' == __name__:
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(main())
