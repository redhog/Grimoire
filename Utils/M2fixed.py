import M2Crypto.SSL, M2Crypto.BIO

# These three are a hack around two bugs in M2Crypto - read of BIO does
# not comform to the standard file-interface of Python,
# and the semantics of the mode argument to makefile() differs from
# the socket-interface.
class BIO(M2Crypto.BIO.BIO):
    def read(self, size = None):
        if size:
            return M2Crypto.BIO.BIO.read(self, size)
        else:
            res = ''
            r = M2Crypto.BIO.BIO.read(self, 1024)
            while r:
                res += r
                r = M2Crypto.BIO.BIO.read(self, 1024)
            return res

class IOBuffer(M2Crypto.BIO.IOBuffer, BIO):
    read = BIO.read

class Connection(M2Crypto.SSL.Connection):
    def makefile(self, mode='rb', bufsize='ignored'):
        r = 'r' in mode or '+' in mode
        w = 'w' in mode or 'a' in mode or '+' in mode
        b = 'b' in mode
        m2mode = ['', 'r'][r] + ['', 'w'][w] + ['', 'b'][b]
        # XXX Need to dup().
        bio = BIO(self.sslbio, _close_cb=self.close)
        return IOBuffer(bio, m2mode)

    def accept(self):
        ssl, addr = M2Crypto.SSL.Connection.accept(self)
        ssl.__class__ = self.__class__
        return ssl, addr
