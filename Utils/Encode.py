import sys

def encode(obj, enc = sys.getdefaultencoding()):
    return unicode(obj).encode(enc)
