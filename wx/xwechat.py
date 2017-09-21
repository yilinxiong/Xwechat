#!/usr/bin/env python

import sys
from wxpy import *
import asyncio
import curses
from ncurses import MainWindow
from time import sleep


@asyncio.coroutine 
def print_msg():
    last_messages = None
    while True:
        try:
            messages = bot.messages
            if last_messages == messages:
                yield from asyncio.sleep(1)
                continue
            yield from asyncio.sleep(1)
            mwin.lwin.messages = mwin.rwin.messages = messages
            mwin.update()
            last_messages = list(messages)
        except (KeyboardInterrupt, SystemExit):
            break


def listener():
    while True:
        try:
            mwin.listener()
        except (KeyboardInterrupt, SystemExit):
            sys.exit()


@asyncio.coroutine
def listener_executor(loop):
    yield from loop.run_in_executor(None, listener)


if __name__ == '__main__':
    bot = Bot(console_qr=True)
    mwin = MainWindow(curses.initscr())
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait([listener_executor(loop), print_msg()]))
    except (KeyboardInterrupt, SystemExit):
        asyncio.gather(*asyncio.Task.all_tasks()).cancel()
        loop.stop()
        loop.close()
        sys.exit()
