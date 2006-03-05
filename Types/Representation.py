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
    def __init__(self, path = [], levels = 0):
        if Grimoire.Utils.isInstance(path, GrimoireReference):
            levels = path['levels']
            path = path['path']
        types.DictType.__init__(self, path=list(path), levels=levels)
    def __parse__(cls, str):
        levels, str = str.split(':')
        path, str = GrimoirePath.__parse__(str)
        return cls(path, int(levels)), str
    def __add__(self, child):
        """If a is rooted at c and b is rooted at a, then a + b
        references b and is rooted at c."""
        if not Grimoire.Utils.isInstance(child, GrimoireReference):
            child = type(self)(child)
        if child['levels'] > len(self['path']):
            levels = self['levels'] + child['levels'] - len(self['path'])
            path = child['path']
        else:
            levels = self['levels']
            path = self['path']
            if child['levels']:
                path = path[:-child['levels']]
            path = path + child['path']
        return type(self)(path, levels)
    def __radd__(self, child):
        return type(self)(child) + self
    def __sub__(self, child):

        """If a and b are both rooted at c, a - b will reference a but
        rooted at b. This _assumes_ a actually resides under b, if
        not, the result is random garbage. Examples:
        3/foo.bar.fie.naja - 3/foo.bar = 0/fie.naja
        3/foo.bar.fie.naja - 3/foo.xxx = 1/bar.fie.naja
        
        And the 'let's just assume things' ones:
        4/xxx.foo.bar.fie.naja - 3/foo.bar = 0/fie.naja
        3/foo.bar.fie.naja - 4/xxx.foo.bar = 0/fie.naja
        
        """
        
        if not Grimoire.Utils.isInstance(child, GrimoireReference):
            child = type(self)(child)

        selfLevels = self['levels']
        selfPath = self['path']
        childLevels = child['levels']
        childPath = child['path']
        
        if selfLevels > childLevels:
            selfPath = selfPath[selfLevels - childLevels:]
        if childLevels > selfLevels:
            childPath = childPath[childLevels - selfLevels:]
        selfLevels = childLevels = min(selfLevels, childLevels)

        # self and child paths are now rooted at the same place
        prefixLen = len(Grimoire.Utils.commonPrefix(selfPath, childPath))
        path = selfPath[prefixLen:]
        levels = len(childPath) - prefixLen
        return type(self)(path, levels)        
    def __rsub__(self, child):
        return type(self)(child) - self
    def __getattr__(self, name):
        return type(self)(self['path'] + [name], self['levels'])

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
