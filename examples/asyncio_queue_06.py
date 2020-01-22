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

# Starting scheduling coro <coroutine object say_after at 0x105349a40>
# Done put <coroutine object say_after at 0x105349a40> coro to queue
# ===========
# hello task 1 has id 1
# Starting scheduling coro <coroutine object say_after at 0x105349990>
# Done put <coroutine object say_after at 0x105349990> coro to queue
# ===========
# hello task 2 has id 2
# [{'id': 1, 'coro': <coroutine object say_after at 0x105349a40>}, {'id': 2, 'coro': <coroutine object say_after at 0x105349990>}]
# finished at 10:16:43
# Got coro: <coroutine object say_after at 0x105349a40>
# Created task: <coroutine object say_after at 0x105349a40>
# ===========
# Got coro: <coroutine object say_after at 0x105349990>
# Created task: <coroutine object say_after at 0x105349990>
# ===========
# hello
# world
