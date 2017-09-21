#!/usr/bin/env python

import sys
from wxpy import *
import asyncio
import curses
from ncurses import MainWindow
from threading import Thread
from multiprocessing import Process, Pool, Event
from time import sleep
from concurrent.futures import ThreadPoolExecutor


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

def rlistener():
    while True:
        try:
            mwin.rlistener()
        except:
            pass

@asyncio.coroutine
def test1(loop):
    yield from loop.run_in_executor(None, listener)


if __name__ == '__main__':
    bot = Bot(console_qr=True)
    mwin = MainWindow(curses.initscr())
    #p1 = Process(name='p1', target=run)
    #p1.start()
    try:
        #p2 = Process(name='p2', target=listener)
        #p2.start()
    
        loop = asyncio.get_event_loop()
        #p1 = asyncio.async(print_msg())
        #loop.run_until_complete(print_msg())
        loop.run_until_complete(asyncio.wait([test1(loop), print_msg()]))
    except (KeyboardInterrupt, SystemExit):
        #p2.join()
        asyncio.gather(*asyncio.Task.all_tasks()).cancel()
        loop.stop()
        loop.close()
        sys.exit()
