import json

from chat import submit_message, get_connection


class InvalidToken(Exception):
    def __str__(self):
        return 'Check the token, the server did not recognize it'


async def authorize(reader, writer, token):

    response = await reader.readline()
    await submit_message(writer, token, 2)

    response = await reader.readline()
    decoded_response = json.loads(response.decode().strip())
    if not decoded_response:
        raise InvalidToken

    return decoded_response['nickname']


async def send_msgs(host, send_port, sending_queue, token):
    async with get_connection(host, send_port) as (reader, writer):
        nickname = await authorize(reader, writer, token)
        print(f'nickname: {nickname}')
        while True:
            msg = await sending_queue.get()
            await submit_message(writer, msg, 2)
