import base64, sha

def getsalt(l = 8):
    f = open('/dev/urandom', 'r')
    salt = f.read(l)
    f.close()
    return salt

def getasciisalt(l = 8):
    return base64.encodestring(getsalt(l))[:l]

def sshaencrypt(str):
    salt = getsalt()
    return base64.encodestring(sha.new(str + salt).digest() + salt)
