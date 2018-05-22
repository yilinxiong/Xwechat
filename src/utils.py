def messages_filter(messages, cols, rows):
    _messages = []
    while True:
        if not messages:
            break
        else:
            from _messages import _CMessage
            total_lines = 0
            item = messages.pop()
            message = _CMessage(item, cols, rows)
            total_lines += message.lines
            if total_lines < int(rows) - 1:
                _messages.append(message)
            else:
                break

    return _messages[::-1]


def ensure_one(found):
    """
    Ensure only one item in the found list
    """
    if not isinstance(found, list):
        raise TypeError('expected list, {} found'.format(type(found)))
    elif not found:
        return None
    elif len(found) > 1:
        raise ValueError('more than one found')
    else:
        return found[0]


def str_len(str):  
    # Caculate the lenght of a string which may contains Chinese
    try:  
        row_l=len(str)  
        utf8_l=len(str.encode('utf-8'))  
        return int((utf8_l-row_l)/2+row_l)
    except:  
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
