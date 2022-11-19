import json

from chat import submit_message
from gui import NicknameReceived


class InvalidToken(Exception):
    def __str__(self):
        return 'Check the token, the server did not recognize it'


async def authorize(reader, writer, token, queues):

    response = await reader.readline()
    await submit_message(writer, token, 2)
    queues['watchdog_queue'].put_nowait(
        'Connection is alive. Prompt before auth'
    )

    response = await reader.readline()
    decoded_response = json.loads(response.decode().strip())
    if not decoded_response:
        raise InvalidToken

    return decoded_response['nickname']


async def send_msgs(reader, writer, token, queues):
    nickname = await authorize(reader, writer, token, queues)
    queues['watchdog_queue'].put_nowait(
        'Connection is alive. Authorization done'
    )
    event = NicknameReceived(nickname)
    queues['status_updates_queue'].put_nowait(event)
    while True:
        msg = await queues['sending_queue'].get()
        await submit_message(writer, msg, 2)
        queues['watchdog_queue'].put_nowait(
            'Connection is alive. Message sent'
        )
