# coding: utf-8
from __future__ import unicode_literals


class WXError(Exception):
    """
    Any exception catches in the subprocess, raise this error
    so that main process can catch it and handle the curses termination
    """
