import asyncio


async def wait(seconds):
    """ Coroutine -- unit of work like thread or process. """
    await asyncio.sleep(seconds)  # asyncio.sleep is awaitable object
    print(f'waited {seconds} seconds')


async def main():
    await wait(1)  # stop and wait coro 1 second. Total - 1 sec
    await wait(2)  # stop and wait coro 2 seconds. Total - 1 + 2 = 3 secs
    await wait(3)  # stop and awit coro 3 seconds. Total - 1 + 2 + 3 = 6 secs
    # main coroutine takes 6 seconds to execute

if __name__ == '__main__':
    event_loop = asyncio.new_event_loop()
    event_loop.run_until_complete(main())
