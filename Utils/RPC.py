
class ServerObject(object):
    __slots__ = ['__serverObjectId', '__weakref__']
    def _getServerObjectId(self, server):
        try:
            return self.__serverObjectId[server]
        except AttributeError:
            self.__serverObjectId = {}
        except KeyError:
            pass
        self.__serverObjectId[server] = server.registerObject(self)
        return self.__serverObjectId[server]
