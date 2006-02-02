import Grimoire.Utils, string, sys, traceback

class Extension(Grimoire.Utils.Wrapper):
    def __init__(self, type, value):
        Grimoire.Utils.Wrapper.__init__(self, (type, value))

class ExtensionType: pass
class Identifier(ExtensionType): pass
class Member(ExtensionType): pass
class Application(ExtensionType): pass
class ParameterName(ExtensionType): pass


class UnserializableError(TypeError):
    def __init__(self, obj):
        self.obj = obj
    def __str__(self):
        return 'Unable to serialize object ' + Grimoire.Utils.objInfo(obj)

class RaiseException(object):
    def __init__(self, exc_type = None, exc_value = None, exc_traceback = None):
        t, v, tr = sys.exc_info()
        self.exc_type = exc_type or t
        self.exc_value = exc_value or v
        self.exc_traceback = exc_traceback or traceback.extract_tb(tr)
