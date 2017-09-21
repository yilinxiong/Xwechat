def parse_msg(messages, rows, cols):
    parsed_msg = []
    if not messages:
        return [('No new messages', 1)]
    origin_msg = [msg for msg in messages]
    total_lines = 0
    for message in origin_msg[::-1]:
        msg_time = message.receive_time.strftime("%Y-%m-%d %H:%M:%S  ")
        message = msg_time+str(message)
        message_lines = int((str_len(message) + int(cols) -1)/int(cols))
        total_lines += message_lines
        if total_lines < int(rows) - 1:
            parsed_msg.insert(0, (message, message_lines))
        else:
            break
    parsed_msg.insert(0, ('New Messages: ', 1))
    return parsed_msg


def parse_chats(messages):
    _chats = []
    if not messages:
        return _chats
    chats = [msg.chat for msg in messages]
    for chat in chats[::-1]:
        if chat not in _chats:
            _chats.append(chat)
    return _chats

def str_len(str):  
    # Caculate the lenght of a string which may contains Chinese
    try:  
        row_l=len(str)  
        utf8_l=len(str.encode('utf-8'))  
        return int((utf8_l-row_l)/2+row_l)
    except:  
        return 0  
    return 0 



def subString(string,length):
    if length >= str_len(string):
                return string
 
    result = ''
    i = 0
    p = 0
 
    while True:
                ch = ord(string[i])
                #1111110x
                if ch >= 252:
                        p = p + 6
                #111110xx
                elif ch >= 248:
                        p = p + 5
                #11110xxx
                elif ch >= 240:
                        p = p + 4
                #1110xxxx
                elif ch >= 224:
                        p = p + 3
                #110xxxxx
                elif ch >= 192:
                        p = p + 2
                else:
                        p = p + 1  
         
                if p >= length:
                        break;
                else:
                        i += 1
 
    return string[0:i]
