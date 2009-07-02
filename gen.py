from string import ascii_letters, digits


chars = '!*.' + digits + ascii_letters + "$-_'(),"


def up(url):
    last = url[-1]
    pos = chars.index(last)
    return url[:-1] + chars[pos+1]


def next(url):
    try:
        return up(url)
    except IndexError:
        if not url:
            return chars[0]
        return next(url[:-1]) + chars[0]


if __name__ == '__main__':
    url = ''
    for n in range(500000):
        url = next(url)
        print url
