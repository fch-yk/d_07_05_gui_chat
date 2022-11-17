import asyncio
import datetime
import logging
import socket
from pathlib import Path

import aiofiles
from async_timeout import timeout

from chat import get_connection
from gui import ReadConnectionStateChanged


async def get_messages_queue(history_path):
    messages_queue = asyncio.Queue()  # type: ignore
    if not Path(history_path).exists():
        return messages_queue

    async with aiofiles.open(history_path, mode='r', encoding='utf-8') as file:
        async for history_line in file:
            messages_queue.put_nowait(history_line.strip())

    return messages_queue


async def save_messages(file_path, queues):
    async with aiofiles.open(file_path, mode='a', encoding='utf-8') as file:
        while True:
            history_line = await queues['history_queue'].get()
            await file.write(f'{history_line}\n')


def reconnect(async_function):
    async def wrap(*args):
        while True:
            try:
                await async_function(*args)
            except (ConnectionError, socket.gaierror) as fail:
                logging.debug('listener: Unable to connect: %s', fail)
                await asyncio.sleep(5)

    return wrap


async def read_chat(reader, queues):

    while True:
        try:
            async with timeout(1):
                message = await reader.readline()
                if reader.at_eof():
                    break
                now = datetime.datetime.now().strftime('%d.%m.%y %H:%M')
                history_line = f'[{now}] {message.decode()}'.strip()
                queues['messages_queue'].put_nowait(history_line)
                queues['history_queue'].put_nowait(history_line)
                queues['watchdog_queue'].put_nowait(
                    'Connection is alive. New message in chat'
                )
        except asyncio.exceptions.TimeoutError:
            queues['watchdog_queue'].put_nowait('1s timeout is elapsed')


@reconnect
async def read_msgs(host, port, queues):
    async with get_connection(host, port) as (reader, _):
        event = ReadConnectionStateChanged.ESTABLISHED
        queues['status_updates_queue'].put_nowait(event)
        await read_chat(reader, queues)
