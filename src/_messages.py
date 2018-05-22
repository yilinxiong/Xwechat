# coding: utf-8
import time

from wxpy.api.messages.message import Message
from wxpy.api.messages.sent_message import SentMessage
from utils import str_len


class _Message(object):
    def __init__(self, msg):
        self.msg = msg
        # Once processed the message, set read to True
        self.msg.read = True

    def __repr__(self):
        return self.text

    @property
    def text(self):
        if isinstance(self.msg, (Message, SentMessage)):
            received_time = self.msg.receive_time.strftime("%Y-%m-%d %H:%M:%S  ")
            message = received_time + str(self.msg)
        else:
            message = self.msg

        return message

    @property
    def timestamp(self):
        received_time = self.msg.receive_time.timetuple()
        timestamp = int(time.mktime(received_time))
        return str(timestamp)

    @property
    def user(self):
        return self.msg.chat.puid


class _CMessage(object):
    def __init__(self, msg, cols, raws=20):
        self.msg = msg
        self.cols = cols
        self.raws = raws
        self._text = ""

    @property
    def text(self):
        raws = int((str_len(self.msg) + int(self.cols) - 1) / int(self.cols))
        if raws > self.raws:
            self._text = self.msg[:100] + "...(Message too long, please check in your phone)"
        else:
            self._text = self.msg

        return self._text

    @property
    def lines(self):
        return int((str_len(self.text) + int(self.cols) - 1) / int(self.cols)) or 1
