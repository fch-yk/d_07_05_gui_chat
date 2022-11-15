
import argparse
import asyncio

import gui
import time

from listen_minechat import read_msgs


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


async def generate_msgs(queue):
    while True:
        queue.put_nowait(f'Ping {time.time()}')
        await asyncio.sleep(1)


async def main():
    args_parser = create_args_parser()
    args = args_parser.parse_args()
    messages_queue = asyncio.Queue()  # type: ignore
    sending_queue = asyncio.Queue()  # type: ignore
    status_updates_queue = asyncio.Queue()  # type: ignore
    await asyncio.gather(
        gui.draw(messages_queue, sending_queue, status_updates_queue),
        read_msgs(args.host, args.listen_port, messages_queue)
    )

if __name__ == '__main__':
    asyncio.run(main())
