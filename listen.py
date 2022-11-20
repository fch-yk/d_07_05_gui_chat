import asyncio
import datetime
import pathlib

import aiofiles


async def get_messages_queue(history_path):
    messages_queue = asyncio.Queue()  # type: ignore
    if not pathlib.Path(history_path).exists():
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


async def read_msgs(reader, queues):

    while True:
        message = await reader.readline()
        if reader.at_eof():
            break
        now = datetime.datetime.now().strftime('%d.%m.%y %H:%M')
        history_line = f'[{now}] {message.decode()}'.strip()
        queues['messages_queue'].put_nowait(history_line)
        queues['history_queue'].put_nowait(history_line)
        queues['watchdog_queue'].put_nowait(
            'Connection is alive: new message in chat'
        )
