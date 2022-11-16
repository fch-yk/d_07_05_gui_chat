import json

from chat import submit_message


async def authorize(reader, writer, token):

    response = await reader.readline()
    await submit_message(writer, token, 2)

    response = await reader.readline()
    decoded_response = json.loads(response.decode().strip())

    return bool(decoded_response), decoded_response.get('nickname')


async def send_msgs(writer, sending_queue):
    while True:
        msg = await sending_queue.get()
        await submit_message(writer, msg, 2)
