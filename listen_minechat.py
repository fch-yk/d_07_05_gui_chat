import asyncio
import datetime
import logging
import socket


from chat import get_connection


def reconnect(async_function):
    async def wrap(host, port, file_path):
        while True:
            try:
                await async_function(host, port, file_path)
            except (ConnectionError, socket.gaierror) as fail:
                logging.debug('listener: Unable to connect: %s', fail)
                await asyncio.sleep(5)

    return wrap


async def read_chat(reader, queue):

    while True:
        message = await reader.readline()
        if reader.at_eof():
            break
        now = datetime.datetime.now().strftime('%d.%m.%y %H:%M')
        history_line = f'[{now}] {message.decode()}'
        queue.put_nowait(history_line.strip())


@reconnect
async def read_msgs(host, port, queue):
    async with get_connection(host, port) as (reader, _):
        await read_chat(reader,  queue)
