import aiohttp
import asyncio
import datetime

old_price = 0.00


async def fetch_prices():
    global old_price
    print(datetime.datetime.now().time())
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.coinlore.com/api/ticker/?id=90') as response:
            response_json = await response.json()
            current_btc_price = float(response_json[0]['price_usd'])
            print(f"Current BTC price: {current_btc_price} USD")
            diff = current_btc_price - old_price
            print(f"Diff: {diff:.2f}")
            print("====================")
            old_price = current_btc_price

        return response_json


def schedule_task():
    current_loop = asyncio.get_event_loop()
    # print(f"id(loop) in schedule_task: {id(loop)}")
    current_loop.create_task(fetch_prices())
    # schedule fetching
    current_loop.call_later(delay=4, callback=schedule_task)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    # print(f"id(loop) in __main__: {id(loop)}")
    loop.call_soon(schedule_task)
    loop.run_forever()



