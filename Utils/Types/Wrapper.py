import sys

class GenericWrapper:
    def __getattr__(self, name):
        try:
            return getattr(self._getValue(), name)
        except AttributeError:
            try:
                return self.__dict__[name]
            except KeyError:
                raise AttributeError(name)
    def __setattr__(self, name, value):
        try:
            setattr(self._getValue(), name, value)
        except AttributeError:
            self.__dict__[name] = value
    def __delattr__(self, name):
        try:
            delattr(self._getValue(), name)
        except AttributeError:
            try:
                del self.__dict__[name]
            except KeyError:
                raise AttributeError(name)
    def __cmp__(self, other):
        if isinstance(other, Wrapper):
            return cmp(self._getValue(), other.value)
        else:
            return cmp(self._getValue(), other)
    def __unicode__(self):
        return unicode(self._getValue())
    def get(self, name, default = None):
        try:
            return self[name]
        except KeyError:
            return default
    def has_key(self, name):
        try:
            self[name]
            return 1
        except KeyError:
            return 0

class Wrapper(GenericWrapper):
    def __init__(self, value):
        self.__dict__['value'] = value
    def _getValue(self):
        return self.value
