#!/usr/bin/env python

import sys
from wxpy import *
import asyncio
import curses
from ncurses import MainWindow


class XWechat(object):
    def __init__(self):
        self.bot = Bot(console_qr=True)
        self.mwin = MainWindow(curses.initscr())
        self.loop = asyncio.get_event_loop()
        self.friends = self.bot.friends()
        self.groups = self.bot.groups()
        self.groups.extend(self.friends)
        self.mwin.rwin.friends = self.groups

    @asyncio.coroutine
    def print_msg(self):
        last_messages = None
        while True:
            try:
                messages = self.bot.messages
                if last_messages == messages:
                    yield from asyncio.sleep(1)
                    continue
                yield from asyncio.sleep(1)
                self.mwin.lwin.messages = self.mwin.rwin.messages = messages
                self.mwin.update()
                # Make sure the cursor will back to the right bottom screen after updating the messages
                if self.mwin.rwin.is_typed:
                    self.mwin.rwin.right_bottom_screen.refresh()
                last_messages = list(messages)
            except (KeyboardInterrupt, SystemExit):
                sys.exit() 

    def listener(self):
        while True:
            try:
                self.mwin.listener()
            except (KeyboardInterrupt, SystemExit):
                sys.exit()

    @asyncio.coroutine
    def listener_executor(self):
        # https://docs.python.org/3/library/asyncio-eventloop.html
        # The listener is a blocking function, calling the listener in a Executor which is pool of threads will avoid blocking other tasks
        yield from self.loop.run_in_executor(None, self.listener)

    def run(self):
        try:
            self.loop.run_until_complete(asyncio.wait([self.listener_executor(), self.print_msg()]))
        except (KeyboardInterrupt, SystemExit):
            #asyncio.gather(*asyncio.Task.all_tasks()).cancel()
            asyncio.wait(*asyncio.Task.all_tasks()).cancel()
            self.loop.stop()
            self.loop.close()
            #sys.exit()


if __name__ == '__main__':
    xwechat = XWechat()
    xwechat.run()
