import types, Grimoire.Utils, Composable

class Representation(Composable.Composable):
    class __metaclass__(types.TypeType):
        def __new__(cls, name, bases, members):
            if '__parse__' in members:
                members['__parse__'] = classmethod(members['__parse__'])
            return types.TypeType.__new__(cls, name, bases, members)
        def __call__(self, *arg, **kw):
            if not kw and len(arg) == 1 and Grimoire.Utils.isInstance(arg[0], types.BaseStringType):
                res, resstr = self.__parse__(*arg, **kw)
                if resstr:
                    raise TypeError("Garbage at end of string", resstr)
                return res
            return types.TypeType.__call__(self, *arg, **kw)


class RepresentationSequence(Composable.Sequence, Representation):
    def __parse__(cls, str):
        return cls(str and str.split(cls.delimiter) or []), ''

class RepresentationReverseSequence(RepresentationSequence):
    def __parse__(cls, str):
        return cls(Grimoire.Utils.Reverse(str.split(cls.delimiter))), ''

class GrimoirePath(RepresentationSequence):
    delimiter = '.'

class GrimoireReference(types.DictType, Representation):
    def __init__(self, levels, path):
        types.DictType.__init__(self, levels=levels, path=path)
    def __parse__(cls, str):
        levels, str = str.split(':')
        path, str = GrimoirePath.__parse__(str)
        return cls(int(levels), path), str

class DN(RepresentationReverseSequence):
    delimiter = ','
  
class UNIXGroup(RepresentationReverseSequence):
    delimiter = '.'

class DNSDomain(RepresentationReverseSequence):
    delimiter = '.'

class EMailAddress(types.DictType, Representation):
    def __init__(self, username, domain):
        types.DictType.__init__(self, username=username, domain=domain)
    def __parse__(cls, str):
        username, str = str.split('@')
        domain, str = DNSDomain.__parse__(str)
        return cls(username, domain), str