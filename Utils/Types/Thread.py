from Grimoire.Utils.Types import Wrapper
import thread


class ThreadLocalData(Wrapper.GenericWrapper):
    def __init__(self, default = None):
        self.__dict__['_data'] = {}
        self.__dict__['_default'] = default
    def _ensure(self):
        if self._default is not None:
            id = thread.get_ident()
            if id not in self._data:
                self._data[id] = self._default
    def _getValue(self):
        return self.get()
    def set(self, data):
        self._data[thread.get_ident()] = data
    def get(self):
        self._ensure()
        return self._data[thread.get_ident()]

class ThreadLocalStack(ThreadLocalData):
    def __init__(self):
        ThreadLocalData.__init__(self, [])
    def __nonzero__(self):
        return len(self)
