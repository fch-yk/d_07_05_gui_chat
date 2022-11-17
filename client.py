
import argparse
import asyncio
import json

import gui
from listen_minechat import get_messages_queue, read_msgs, save_messages
from send_minechat import InvalidToken, send_msgs


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


async def main():
    args_parser = create_args_parser()
    args = args_parser.parse_args()

    with open(args.token_path, 'r', encoding="UTF-8") as token_file:
        token = json.load(token_file)['account_hash']

    queues = {
        'messages_queue': await get_messages_queue(args.history_path),
        'history_queue': asyncio.Queue(),  # type: ignore
        'sending_queue': asyncio.Queue(),  # type: ignore
        'status_updates_queue': asyncio.Queue(),  # type: ignore
    }

    await asyncio.gather(
        gui.draw(queues),
        read_msgs(args.host, args.listen_port, queues),
        save_messages(args.history_path, queues),
        send_msgs(args.host, args.send_port, token, queues),
    )

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except InvalidToken:
        gui.show_invalid_token_message()
