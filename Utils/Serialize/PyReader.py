import Grimoire.Utils, Types, string, types, unicodedata, sys, StringIO

debugRead = 0
debugInput = 0

try:
    import psyco
    havePsyco = True
except ImportError:
    havePsyco = False
    
class Buffer(object):
    def __new__(cls, file, maxsize = 8192):
        if hasattr(file, 'recv'):
            bufferClass = SocketBuffer
        elif hasattr(file, 'read'):
            bufferClass = FileBuffer
        else:
            bufferClass = StrBuffer
        return object.__new__(bufferClass, file, maxsize)
    def __init__(self, file, maxsize = 8192):
        self.file = file
        self.buf = ''
        self.pos = 0
        self.len = 0
        self.maxsize = maxsize
    def advance(self, nr):
        self.extend(nr)
        self.pos += nr
        self.len -= nr
    def cut(self, nr = None):
        n = nr
        if n is None:
            n = self.len
        else:
            self.extend(n)
        res = self.buf[self.pos:self.pos + n]
        self.advance(n)
        return res
    def containsMultiple(self, char, nr, at = 0):
        for pos in xrange(0, nr):
            rpos = at + pos
            if not self.extend(rpos + 1, False):
                return False
            elif self.buf[self.pos + rpos] != char:
                return False
        return True
    def contains(self, str, at = 0):
        for pos in xrange(0, len(str)):
            rpos = at + pos
            if not self.extend(rpos + 1, False):
                return False
            if self.buf[self.pos + rpos] != str[pos]:
                return False
        return True

class SocketBuffer(Buffer):
    def recv(self, nr):
        return self.file.recv(nr)
    def extend(self, nr, noEOF = 1):
        if nr > self.len:
            if self.pos >= self.maxsize:
                self.buf = self.buf[self.pos:]
                self.pos = 0
            while nr > self.len:
                r = self.recv(max(nr, self.maxsize))
                self.buf += r
                self.len += len(r)
                if debugInput:
                    sys.stderr.write(r)
                    sys.stderr.flush()
                if not r:
                    break
            if nr > self.len:
                if noEOF:
                    raise IOError('End of file')
                else:
                    return False
        return True

class FileBuffer(Buffer):
    def extend(self, nr, noEOF = 1):
        if nr > self.len:
            if self.pos >= self.maxsize:
                self.buf = self.buf[self.pos:]
                self.pos = 0
            r = self.file.read(nr - self.len)
            if debugInput:
                sys.stderr.write(r)
                sys.stderr.flush()
            self.buf += r
            self.len += len(r)
            if nr > self.len:
                if noEOF:
                    raise IOError('End of file')
                else:
                    return False
        return True

class StrBuffer(Buffer):
    def __init__(self, file, maxsize = 8192):
        Buffer.__init__(self, file, maxsize)
        self.buf = file
        self.len = len(file)
    def extend(self, nr, noEOF = 1):
        if nr > self.len:
            if noEOF:
                raise IOError('End of file')
            else:
                return False
        return True


singleCharEscape = {'a': '\a',
                    'b': '\b',
                    'f': '\f',
                    'n': '\n',
                    'r': '\r',
                    't': '\t',
                    'v': '\v',
                    }

# Read a string
def readStr(f):
    f.extend(2)
    start = f.buf[f.pos]
    f.advance(1)
    startlen = 1
    if f.containsMultiple(start, 2):
        startlen = 3
        f.advance(2)
    res = ''
    escaped = 0
    start0 = start[0]
    pos = 0
    while 1:
        if f.containsMultiple(start, startlen, pos):
            if escaped:
                pos += startlen
                escaped = 0
                continue
            res += f.cut(pos)
            f.advance(startlen)
            return res
        if f.buf[f.pos + pos] == '\\':
            res += f.cut(pos)
            f.advance(1) # Skip '\'
            pos = 0
            escaped = 1
            continue
        if escaped:
            escaped = 0
            res += f.cut(pos)
            c = f.cut(1)
            pos = 0
            if c == '\n':
                continue
            elif c in singleCharEscape:
                res += singleCharEscape[c]
                continue
            elif c == 'N':
                f.advance(1) # skip '{'
                ln = 1
                while 1:
                    f.extend(ln + 1)
                    if f.buf[f.pos + ln] == '}':
                        break
                    ln += 1
                res += unicodedata.lookup(f.cut(ln)).encode('utf-8')
                f.advance(1) # skip '}'
                continue
            elif c == 'u':
                res += unichr(int('0x' + f.cut(4), 0)).encode('utf-8')
                continue
            elif c == 'U':
                res += unichr(int('0x' + f.cut(8), 0)).encode('utf-8')
                continue
            elif c in string.digits[:8]:
                res += chr(int('0' + c + f.cut(2), 0))
                continue
            elif c == 'x':
                res += chr(int('0x' + f.cut(2), 0))
                continue
        pos += 1

# Read an integer or floating-point number
def readNum(f):
    pos = 0
    isf = 0
    isl = 0
    while 1:
        if not f.extend(pos + 1, False):
            break
        c = f.buf[f.pos + pos]
        if c in ',:=<{[()]}>' + string.whitespace:
            break
        elif c in ('F', 'f', '.'):
            isf = 1
        elif c in ('L', 'l'):
            isl = 1
        pos += 1
    res = f.cut(pos)
    if isf:
        return float(res)
    elif isl:
        return long(res)
    else:
        return int(res)

# Read an indetifier
def readIdentifier(f):
    pos = 0
    res = ''
    while 1:
        if not f.extend(pos + 1, False):
            res += f.cut()
            break;
        c = f.buf[f.pos + pos]
        if c in '.,:=<{[()]}>' + string.whitespace:
            res += f.cut(pos)
            break
        elif c == '\\':
            res += f.cut(pos)
            f.advance(1)
            pos = 1
        else:
            pos += 1
    if res == 'None':
        return None
    elif res == 'True':
        return True
    elif res == 'False':
        return False
    return Types.Extension(Types.Identifier, res)

# For now, don't do any conversion...
def readUnicodeOrId(f):
    if f.contains("u'") or f.contains('u"') or f.contains("U'") or f.contains('U"'):
        f.advance(1)
        return readStr(f).decode('utf-8')
    else:
        return readIdentifier(f)

parseMap = Grimoire.Utils.InMap(
    {"'\"": readStr,
     string.digits + '+-.': readNum,
     })
parseMapDefault = readUnicodeOrId


def internalRead(f, inParens = False, inMemberList = False):
    res = []
    multi = (inParens and inParens != '(')
    separated = True
    while 1:
        if not f.extend(1, noEOF=inParens):
            break
        c = f.buf[f.pos]
        if c in '\r\n':
            if not res or inParens:
                f.advance(1)
                continue
            break
        if c in ')]}>':
            if inParens:
                f.advance(1)
            break
        elif c in string.whitespace:
            f.advance(1)
            continue
        elif c == ',':
            if not inParens:
                break
            f.advance(1)
            multi = True
            separated = True
            continue
        elif c == ':':
            f.advance(1)
            res[-1] = (res[-1], internalRead(f))
            continue
        elif c == '=':
            f.advance(1)
            res[-1] = Types.Extension(Types.ParameterName, (res[-1].value[1], internalRead(f)))
            continue
        elif c == '.':
            if inMemberList:
                if not res:
                    raise IOError('Premature end of file reached')
                break
            f.advance(1)
            res[-1] = Types.Extension(Types.Member, (res[-1], internalRead(f, inMemberList = True)))
            continue
        elif c == '(':
            if not separated and inMemberList:
                break
            f.advance(1)
            if not separated:
                # Parameter lists are still lists, even if they contain only one element...
                c = '['
            value = internalRead(f, c)
            if not separated:
                res[-1] = Types.Extension(Types.Application, (res[-1], value))
                continue
        elif c in '[{<':
            f.advance(1)
            value = internalRead(f, c)
        else:
            try:
                parser = parseMap[c]
            except KeyError:
                parser = parseMapDefault
            value = parser(f)
        separated = False
        res.append(value)
    if not multi:
        if not res:
            if inParens == '(':
                res = ()
            else:
                raise IOError('End of file')
        else:
            res = res[0]
    elif inParens == '(':
        res = tuple(res)
    elif inParens == '{':
        res = dict(res)
    elif inParens == '<':
        res = Types.Extension(*res)
    return res

def read(f, inParens = False, inMemberList = False):
    return internalRead(f, inParens, inMemberList)

if havePsyco:
    psyco.bind(Buffer)
    psyco.bind(SocketBuffer)
    psyco.bind(FileBuffer)
    psyco.bind(readStr)
    psyco.bind(readNum)
    psyco.bind(readIdentifier)
    psyco.bind(readUnicodeOrId)
    psyco.bind(internalRead)
    psyco.bind(read)
