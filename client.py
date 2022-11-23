
import argparse
import asyncio
import json
import logging
import socket
import time
import tkinter


import chat
import gui
import listen
import send


def create_args_parser():
    parser = argparse.ArgumentParser(description='Chat client.')

    parser.add_argument(
        '--debug_mode',
        help='Turn on debug mode',
        action="store_true",
    )

    parser.add_argument(
        '--host',
        default='minechat.dvmn.org',
        metavar='{host}',
        help='The chat host, minechat.dvmn.org by default',
    )

    parser.add_argument(
        '--listen_port',
        metavar='{listen port}',
        default=5000,
        help='The listen chat port, 5000 by default',
        type=int,
    )

    parser.add_argument(
        '--send_port',
        metavar='{send port}',
        default=5050,
        help='The send chat port, 5050 by default',
        type=int,
    )

    parser.add_argument(
        '--token_path',
        default='token.json',
        metavar='{token path}',
        help='A path to your token file, token.json by default',
    )

    parser.add_argument(
        '--history_path',
        default='history.txt',
        metavar='{history path}',
        help='A path to history file, history.txt by default',
    )

    return parser


async def watch_for_connection(queues):
    while True:
        try:
            async with asyncio.timeout(1):
                line = await queues['watchdog_queue'].get()
                logger = logging.getLogger("watchdog_logger")
                logger.debug('[%s] %s', time.time(), line)
        except TimeoutError as timeout_error:
            raise ConnectionError('Connection error') from timeout_error


async def process_connection_error(queues):
    logging.debug('Unable to connect')
    set_connections_statuses('CLOSED', queues)
    await asyncio.sleep(5)


def reconnect(async_function):
    async def wrap(args, token, queues):
        while True:
            try:
                await async_function(args, token, queues)
            except* ConnectionError:
                await process_connection_error(queues)
            except* socket.gaierror:
                await process_connection_error(queues)
    return wrap


def set_connections_statuses(status, queues):
    states = (
        gui.ReadConnectionStateChanged,
        gui.SendingConnectionStateChanged
    )
    for state in states:
        queues['status_updates_queue'].put_nowait(state[status])


async def ping_send(queues):
    while True:
        queues['sending_queue'].put_nowait('')
        await asyncio.sleep(0.5)


@reconnect
async def handle_connection(args, token, queues):
    set_connections_statuses('INITIATED', queues)
    async with chat.get_connections(
        args.host,
        args.listen_port,
        args.send_port
    ) as (listen_reader, _, send_reader, send_writer):
        set_connections_statuses('ESTABLISHED', queues)
        async with asyncio.TaskGroup() as task_group:
            task_group.create_task(listen.read_msgs(listen_reader, queues))
            task_group.create_task(
                send.send_msgs(send_reader, send_writer, token, queues)
            )
            task_group.create_task(watch_for_connection(queues))
            task_group.create_task(ping_send(queues))


async def main():
    args_parser = create_args_parser()
    args = args_parser.parse_args()

    with open(args.token_path, 'r', encoding="UTF-8") as token_file:
        token = json.load(token_file)['account_hash']

    if args.debug_mode:
        logging.basicConfig(level=logging.DEBUG)

    queues = {
        'messages_queue': await listen.get_messages_queue(args.history_path),
        'history_queue': asyncio.Queue(),  # type: ignore
        'sending_queue': asyncio.Queue(),  # type: ignore
        'status_updates_queue': asyncio.Queue(),  # type: ignore
        'watchdog_queue': asyncio.Queue(),  # type: ignore
    }

    async with asyncio.TaskGroup() as task_group:
        task_group.create_task(handle_connection(args, token, queues))
        task_group.create_task(gui.draw(queues))
        task_group.create_task(listen.save_messages(args.history_path, queues))


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except* chat.InvalidToken:
        log_text = 'Check the token, the server did not recognize it.'
        tkinter.messagebox.showerror(
            'Incorrect token',
            log_text
        )
        logging.error(log_text)
    except* KeyboardInterrupt:
        logging.debug('Keyboard interrupt')
    except* tkinter.TclError:
        logging.debug('The chat console was closed')
    except* asyncio.exceptions.CancelledError:
        logging.debug('The chat was cancelled')
