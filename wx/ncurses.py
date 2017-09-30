import re
import sys
import curses
from math import ceil
from utils import parse_msg, parse_chats, str_len


class CWindow(object):
    def __init__(self, std_screen):
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

    def init_window(self, *args, **kwargs):
        pass

    def display(self, *args, **kwargs):
        pass


class LeftWindow(CWindow):
    def __init__(self, std_screen):
        super(LeftWindow, self).__init__(std_screen)
        self.left_rows = None
        self.left_cols = None
        self.left_screen = None
        self.messages = None
        self.init_window()

    def init_window(self):
        self.left_rows = self.total_rows - 2
        self.left_cols = int(self.total_cols / 2) - 2
        self.left_screen = self.window.subwin(self.left_rows, self.left_cols, self.pos_x + 1, self.pos_y + 1)

    def display(self):
        self.left_screen.leaveok(1)
        self.left_screen.clear()
        parsed_messages = parse_msg(self.messages, self.left_rows, self.left_cols)
        n = 0
        for (msg, lines) in parsed_messages:
            self.left_screen.addstr(n, 0, msg)
            n += lines
        self.left_screen.refresh()


class RightWindow(CWindow):
    def __init__(self, std_screen):
        super(RightWindow, self).__init__(std_screen)
        self.right_rows = None
        self.right_cols = None
        self.right_pos_x = None
        self.right_pos_y = None
        self.right_screen = None
        self.right_top_cols = None
        self.right_top_rows = None
        self.right_bottom_cols = None
        self.right_bottom_rows = None
        self.right_top_screen = None
        self.right_bottom_screen = None
        self.messages = None
        self.friends = None
        self._friends = None
        self.chater = None
        self.active = False
        self.selected = 0
        self.page = 0
        self.total_page = 0
        self.is_typed = False
        self.list_all = False
        self.init_window()
        self.prepare_chat_window()

    def init_window(self):
        self.right_rows = self.total_rows - 2
        self.right_cols = self.total_cols - int(self.total_cols / 2) - 3
        self.right_pos_x = self.pos_x + 1
        self.right_pos_y = self.pos_y + int(self.total_cols / 2) + 2
        self.right_screen = self.window.derwin(self.right_rows,
                                               self.right_cols,
                                               self.right_pos_x,
                                               self.right_pos_y)
        self.right_screen.leaveok(1)

    def prepare_chat_window(self):
        self.right_top_cols = self.right_bottom_cols = self.right_cols
        self.right_bottom_rows = 6
        self.right_top_rows = self.right_rows - 6
        self.right_top_screen = self.right_screen.derwin(self.right_top_rows,
                                                         self.right_top_cols,
                                                         0,
                                                         0)
        self.right_bottom_screen = self.right_screen.derwin(self.right_bottom_rows,
                                                            self.right_bottom_cols,
                                                            self.right_top_rows,
                                                            0)
        # Makes the cursor only visible in the bottom screen
        self.right_top_screen.leaveok(1)
        self.right_bottom_screen.leaveok(0)
        self.right_bottom_screen.keypad(0)

    def pre_display(self):
        self._friends = None
        self.right_screen.clear()
        if not self.list_all:
            friends = parse_chats(self.messages)
        else:
            friends = self.friends

        if not friends:
            if self.list_all:
                show_msg = "Couldn't fetch friends list!!!"
            else:
                show_msg = "No new chats:"
            self.right_screen.addstr(0, 0, show_msg)
            self.right_screen.refresh()
            return False
        else:
            if self.list_all:
                msg = 'Friends list(' + str(len(friends)) + '):'
            else:
                msg = 'Chats list(' + str(len(friends)) + '):'
            self.right_screen.addstr(0, 0, msg)

        page_rows = self.right_rows - 2
        self.total_page = ceil(len(friends) / page_rows) - 1
        if len(friends) >= page_rows:
            if self.page > self.total_page:
                self.page = self.total_page
            elif self.page < 0:
                self.page = 0
            self._friends = friends[page_rows * self.page:page_rows * (self.page + 1)]
        else:
            self._friends = friends
        return True

    def display(self):
        if not self.is_typed:
            result = self.pre_display()
            if not result:
                return

            if self.selected >= len(self._friends):
                self.selected = len(self._friends) - 1
            elif self.selected < 0:
                self.selected = 0

            n = 1
            for index, friend in enumerate(self._friends):
                if index == self.selected:
                    mode = curses.A_REVERSE
                else:
                    mode = curses.A_NORMAL
                self.right_screen.addstr(n, 0, str(n) + ': ' + friend.name, mode)
                n += 1
            self.right_screen.addstr(self.right_rows - 1, 0, '<- Page %d/%d ->' % (self.page+1, self.total_page+1))
            self.right_screen.refresh()
        else:
            self.display_chater_msg()

    def display_chater_msg(self):
        msg = parse_msg(self.messages, self.right_top_rows, self.right_top_cols, self.chater)
        self.right_top_screen.clear()
        n = 0
        for (msg, lines) in msg:
            self.right_top_screen.addstr(n, 0, msg)
            n += lines
        self.right_top_screen.refresh()

    def listener(self, key):
        if key == curses.KEY_DOWN:
            self.selected += 1
            self.display()
        elif key == curses.KEY_UP:
            if self.selected >= 1:
                self.selected -= 1
            else:
                self.selected = 0
            self.display()
        elif key in [ord('a'), ord('A')]:
            self.list_all = True
            self.selected = 0
            self.page = 0
            self.display()
        elif key == curses.KEY_LEFT:
            # Only can be use in display all
            if self.list_all:
                self.page -= 1
                self.display()
        elif key == curses.KEY_RIGHT:
            # Only can be use in display all
            if self.list_all:
                self.page += 1
                self.display()
        elif key in [ord('b'), ord('B')]:
            self.list_all = False
            self.selected = 0
            self.page = 0
            self.display()
        elif key in [curses.KEY_ENTER, ord('\n'), 10]:
            if self._friends:
                self.chat()
        elif key in [27, curses.KEY_HOME]:         # Pressed ESC or HOME key
            self.list_all = False
            self.selected = 0
            curses.noecho()
            curses.curs_set(0)
            self.display()

    def chat(self):
        self.right_screen.clear()
        self.right_screen.refresh()
        self.chater = self._friends[self.selected]
        self.is_typed = True
        self.display_chater_msg()
        # Display the input characters and make the blinking cursor visible so that we can know where the cursor is
        # This is helpful while using the backspace to delete the typied characters
        curses.echo()
        curses.curs_set(1)
        while self.is_typed:
            # Keep waiting for user to input the characters
            self.right_bottom_screen.clear()
            # Print border to separate the bottom and top screens
            self.right_bottom_screen.addstr(0, 0, '-' * self.right_cols)
            self.right_bottom_screen.addstr(1, 0, self.chater.name + ':')
            self.right_bottom_screen.refresh()
            msg = self.right_bottom_screen.getstr(1, str_len(self.chater.name) + 2)
            # Only when the messages is not empty and doesn't contain ESC key we send the messages to friend,
            #   in other words, if we don't want to send the messages we typed,
            #     just press ESC key to finish typing and then press Enter key,
            #       it will go back to the displaying messages page.
            # Moreover, if we want to revoke what we have typed, just press DELETE key and then press Enter key,
            #   it will clear what you have typed and wait for you to type messages
            if msg and b'\x1b[3~' in msg:          # messages contain DELETE key
                continue
            elif msg and not re.search(b'\x1b$', msg):          # messages not contain ESC key
                self.chater.send(msg.decode('utf8'))
                continue
            else:
                # If not input anything, then back to the chats list page so that we can re-choose the chat to send messages
                self.is_typed = False
                # Do not display the blinking cursor and pressed key while not sending the messages
                # Change back all curses settings and return back to the original page
                curses.noecho()
                curses.curs_set(0)
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


