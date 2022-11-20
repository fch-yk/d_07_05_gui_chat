import asyncio
from contextlib import asynccontextmanager


class InvalidToken(Exception):
    def __str__(self):
        return 'Check the token, the server did not recognize it'


@asynccontextmanager
async def get_connection(host, port):
    reader, writer = await asyncio.open_connection(
        host=host,
        port=port
    )
    try:
        yield reader, writer
    finally:
        writer.close()
        await writer.wait_closed()


@asynccontextmanager
async def get_connections(host, listen_port, send_port):
    listen_reader, listen_writer = await asyncio.open_connection(
        host=host,
        port=listen_port
    )
    send_reader, send_writer = await asyncio.open_connection(
        host=host,
        port=send_port
    )
    try:
        yield listen_reader, listen_writer, send_reader, send_writer
    finally:
        listen_writer.close()
        await listen_writer.wait_closed()
        send_writer.close()
        await send_writer.wait_closed()


async def submit_message(writer, message, new_lines_number):
    message_to_submit = message.replace('\n', '')
    message_to_submit += '\n'*new_lines_number
    message_to_submit = message_to_submit.encode()
    writer.write(message_to_submit)
    await writer.drain()
