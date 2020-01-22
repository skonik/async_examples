import asyncio
import time


class Scheduler:
    task_id = 0

    def __init__(self, loop, queue_size=5):
        self._loop = loop
        self.queue = asyncio.Queue(maxsize=queue_size, loop=loop)
        self.tasks = []

    async def schedule(self, coro):
        print('Starting scheduling coro {}'.format(coro))
        await self.queue.put(coro)
        print('Done put {} coro to queue'.format(coro))
        print('===========')

        self.task_id += 1
        self.tasks.append(
            {
                'id': self.task_id,
                'coro': coro
            }
        )

        return self.task_id

    async def monitor_queue(self):
        coro = True
        while coro:
            coro = await self.queue.get()
            if not coro:
                break
            print('Got coro: {}'.format(coro))
            self._loop.create_task(coro)
            print('Created task: {}'.format(coro))
            print('===========')


async def say_after(delay, what):
    await asyncio.sleep(delay)
    print(what)


async def main():
    loop = asyncio.get_event_loop()
    scheduler = Scheduler(loop, 5)

    loop.create_task(scheduler.monitor_queue())
    hello_task_id_1 = await scheduler.schedule(say_after(4, 'hello'))
    print('hello task 1 has id {}'.format(hello_task_id_1))
    print('hello task 1 has status {}'.format(scheduler[hello_task_id_1]['coro'].))
    hello_task_id_2 = await scheduler.schedule(say_after(5, 'world'))
    print('hello task 2 has id {}'.format(hello_task_id_2))
    print(scheduler.tasks)

    print(f"finished at {time.strftime('%X')}")

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.run_forever()
