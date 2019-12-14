import asyncio


async def wait(seconds):
    """ Coroutine -- unit of work like thread or process. """
    await asyncio.sleep(seconds)  # asyncio.sleep is awaitable object
    print(f'waited {seconds} seconds')


async def main():
    # get current eventloop instance
    current_loop = asyncio.get_event_loop()
    current_loop.create_task(wait(1))  # Create independent unit of work and schedule (like parallel thread/process)
    current_loop.create_task(wait(2))
    current_loop.create_task(wait(3))
    # Without the code below main coroutine will end and event loop will be closed.
    # But we have running tasks that were not done yet. That will cause errors.
    # task = current_loop.create_task(wait(3))
    # await task

    print('done main')


if __name__ == '__main__':
    event_loop = asyncio.new_event_loop()
    # event_loop.set_debug(True)
    event_loop.run_until_complete(main())
