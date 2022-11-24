
import asyncio
import logging
import tkinter
from tkinter import ttk
from tkinter import messagebox
import functools

import chat


async def register(reader, writer, token_path, nickname):
    response = await reader.readline()
    logging.debug('response: %s', response.decode().strip())

    await chat.submit_message(writer, '', 1)
    logging.debug('submit: the token request')

    response = await reader.readline()
    logging.debug('response: %s', response.decode().strip())

    await chat.submit_message(writer, nickname, 1)
    logging.debug('submit: the nickname: %s', nickname)

    response = await reader.readline()
    decoded_response = response.decode().strip()
    logging.debug('response: %s', decoded_response)

    with open(token_path, "w", encoding="UTF-8") as token_file:
        token_file.write(decoded_response)


async def get_registered(nickname, host, port, token_path):
    async with chat.get_connection(host, port) as (reader, writer):
        await register(reader, writer, token_path, nickname)


def click_register(entries, debug_mode):
    nickname = entries['nickname'].get()
    if not nickname:
        messagebox.showerror('Error', 'Fill the nickname!')
        return

    if debug_mode.get():
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(levelname)s [%(asctime)s]  %(message)s'
        )
    asyncio.run(
        get_registered(
            entries['nickname'].get(),
            entries['host'].get(),
            int(entries['port'].get()),
            entries['token_path'].get(),
        )
    )
    messagebox.showinfo('Info', 'Registered!')


def set_entry(label_text, default=''):
    frame = ttk.Frame(borderwidth=0, relief=tkinter.SOLID, padding=[8, 10])

    label = ttk.Label(frame, text=label_text)
    label.pack(anchor=tkinter.NW)

    entry = ttk.Entry(frame)
    entry.pack(anchor=tkinter.NW, expand=True, fill=tkinter.X)
    entry.insert(0, default)

    frame.pack(anchor=tkinter.NW, fill=tkinter.X, padx=5, pady=5)
    return entry


def main():
    root = tkinter.Tk()
    root.title('Register in the chat')
    root.geometry('300x400+300+300')

    entries = {
        'nickname': set_entry('Nickname:'),
        'host': set_entry('Host:', 'minechat.dvmn.org'),
        'port': set_entry('Port:', '5050'),
        'token_path': set_entry('Token path:', 'token.json'),
    }
    debug_mode = tkinter.IntVar()
    debug_checkbutton = ttk.Checkbutton(text="Debug mode", variable=debug_mode)
    debug_checkbutton.pack(padx=6, pady=6, anchor=tkinter.NW)

    click_handler = functools.partial(
        click_register,
        entries=entries,
        debug_mode=debug_mode,
    )
    btn = ttk.Button(text='Register', command=click_handler)
    btn.pack(side=tkinter.BOTTOM, fill=tkinter.X)

    root.mainloop()


if __name__ == '__main__':
    main()
