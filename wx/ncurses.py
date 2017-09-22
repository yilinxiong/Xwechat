import curses
import sys
from utils import parse_msg, parse_chats, str_len


class CWindow(object):
    def __init__(self, std_screen, pos_x=0, pos_y=0):
        self.window = std_screen
        self.pos_x, self.pos_y = 0, 0
        self.total_rows, self.total_cols = self.window.getmaxyx()

    def print_border(self):
        self.window.clear()
        for idx in range(1, self.total_rows - 1):
            self.window.addstr(idx, 0, '|')
            self.window.addstr(idx, int(self.total_cols/2) + 1, '|')
            self.window.addstr(idx, self.total_cols - 1, '|')

        self.window.addstr(0, 1, '-' * (self.total_cols - 2))
        self.window.addstr(self.total_rows - 1, 1, '-' * (self.total_cols - 2))
        self.window.refresh()

    def display(self, *args, **kwargs):
        pass

    @staticmethod
    def destroy():
        curses.initscr()
        curses.nocbreak()
        curses.echo()
        curses.endwin()


class LeftWindow(CWindow):
    def __init__(self, std_screen, pos_x=0, pos_y=0):
        super(LeftWindow, self).__init__(std_screen)
        self.left_screen, self.left_rows, self.left_cols = self.create()
        self.messages = None

    def create(self):
        left_rows = self.total_rows - 2
        left_cols = int(self.total_cols / 2) - 2
        left_screen = self.window.subwin(left_rows, left_cols, self.pos_x + 1, self.pos_y + 1)
        return left_screen, left_rows, left_cols

    def display(self):
        self.left_screen.clear()
        parsed_messages = parse_msg(self.messages, self.left_rows, self.left_cols)
        n = 0
        for (msg, lines) in parsed_messages:
            self.left_screen.addstr(n, 0, msg)
            n += lines
        self.left_screen.refresh()


class RightWindow(CWindow):
    def __init__(self, std_screen, pos_x=0, pos_y=0):
        super(RightWindow, self).__init__(std_screen)
        self.right_screen, self.right_rows, self.right_cols, self.pos_y, self.pos_x= self.create()
        self.chats = None
        self._chats = None
        self.active = False
        self.selected = 0
        self.messages = None
        self.is_typed = False

    def create(self):
        right_rows = self.total_rows - 2
        right_cols = self.total_cols - int(self.total_cols / 2) - 3
        pos_x = self.pos_x + 1
        pos_y = self.pos_y + int(self.total_cols / 2) + 2
        right_screen = self.window.derwin(right_rows, right_cols, pos_x, pos_y)
        return right_screen, right_rows, right_cols, pos_y, pos_x

    def display(self):
        if not self.is_typed:
            self.right_screen.clear()
            #self.right_screen.leaveok(0)
            self.right_screen.addstr(0, 0, 'Recent chats:')
            self.chats = parse_chats(self.messages)
            if not self.chats:
                self.right_screen.refresh()
                return
            n = 1
            if len(self.chats) >= self.right_rows:
                self._chats = chats[len(self.chats)-self.right_rows-1:]
            else:
                self._chats = self.chats
            if self.selected >= len(self._chats):
                self.selected = len(self._chats) - 1
            elif self.selected < 0:
                self.selected = 0
            for index, chat in enumerate(self._chats):
                if index == self.selected:
                    mode = curses.A_REVERSE
                else:
                    mode = curses.A_NORMAL
                self.right_screen.addstr(n, 0, str(n) + ': ' + chat.name, mode)
                n += 1
            self.right_screen.refresh()
      
    def listener(self, key):
        if key in [curses.KEY_DOWN, 66]:
            self.selected += 1
            self.display()
        elif key in [curses.KEY_UP, 65]:
            if self.selected >= 1:
                self.selected -= 1
            else:
                self.selected = 0
            self.display()
        elif key in [curses.KEY_ENTER, ord('\n'), 10]:
            self.chat()

    def chat(self):
        if self._chats is None:
            self.display()
        self.is_typed = True
        chater = self._chats[self.selected]
        while self.is_typed:
            self.right_screen.clear()
            self.right_screen.addstr(0, 0, chater.name + ':')
            self.right_screen.refresh()
            curses.echo()
            msg = self.right_screen.getstr(0, str_len(chater.name) + 2)
            if msg:
                chater.send(msg.decode('utf8'))
                continue
            else:
                self.is_typed = False
                curses.noecho()
                self.display()

class MainWindow(object):
    def __init__(self, std_screen):
        try:
            self.screen = std_screen
            self.selected = 0
            curses.cbreak()
            curses.noecho()
            curses.curs_set(0)
            self.main = self.screen.subwin(0, 0)
            self.main.keypad(1)
            self.main.nodelay(1)
            self.cwin = CWindow(self.screen)
            self.cwin.print_border()
            self.lwin = LeftWindow(self.screen)
            self.lwin.display()
            self.rwin = RightWindow(self.screen)
            self.rwin.display()
            
        except (KeyboardInterrupt, SystemExit):
            self.destroy()

    def update(self):
        self.lwin.display()
        self.rwin.display()
    
    def listener(self):
        key = self.main.getch()
        if key in [ord('q'), ord('Q')]:
            self.destroy()
            sys.exit()
        else:
            self.rwin.listener(key)

    @staticmethod 
    def destroy():
        curses.initscr()
        curses.nocbreak()
        curses.echo()
        curses.endwin()

