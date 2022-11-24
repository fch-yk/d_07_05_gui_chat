import json

import chat
import gui
from chat import submit_message


async def authorize(reader, writer, token, queues):

    response = await reader.readline()
    await chat.submit_message(writer, token, 2)
    queues['watchdog_queue'].put_nowait(
        'Connection is alive: prompt before auth'
    )

    response = await reader.readline()
    decoded_response = json.loads(response.decode().strip())
    if not decoded_response:
        raise chat.InvalidToken

    return decoded_response['nickname']


async def send_msgs(reader, writer, token, queues):
    nickname = await authorize(reader, writer, token, queues)
    queues['watchdog_queue'].put_nowait(
        'Connection is alive: Authorization done'
    )
    event = gui.NicknameReceived(nickname)
    queues['status_updates_queue'].put_nowait(event)
    while True:
        msg = await queues['sending_queue'].get()
        await submit_message(writer, msg, 2)
        reply = await reader.readline()
        if not reply:
            raise ConnectionError
        if not msg:
            msg = 'ping'
        queues['watchdog_queue'].put_nowait(
            f'Connection is alive: {msg} message sent'
        )
