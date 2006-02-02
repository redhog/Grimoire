import os, types, Grimoire.Utils, Representation

class NoPartError(TypeError): pass

class AbstractPath(Representation.Representation): pass

# header+
# +relative+
# +trailer

class PathCombination(types.DictType, AbstractPath):
    def __parse__(cls, str):
        resdict = {}
        for part in ('header', 'relative', 'trailer'):
            try:
                resdict[part], str = getattr(cls, '__' + part + '__').__parse__(str)
            except NoPartError:
                pass
        return cls(resdict), str

    def __add__(self, other):
        if 'trailer' in self:
            raise TypeError('Unable to add more path after trailer')
        resdict = {}
        resdict.update(self)
        if Grimoire.Utils.isInstance(other, types.BaseStringType):
            other = type(self)(other)
        if Grimoire.Utils.isInstance(self, type(other)):
            if 'header' in other:
                raise TypeError('Unable to add more path before header')
            if 'relative' in other:
                if 'relative' in resdict:
                    resdict['relative'] = resdict['relative'] + other['relative']
                else:
                    resdict['relative'] = other['relative']
            if 'trailer' in other:
                resdict['trailer'] = other['trailer']
        elif Grimoire.Utils.isInstance(other, types.ListType, types.TupleType):
            if 'relative' in resdict:
                resdict['relative'] = resdict['relative'] + other
            else:
                resdict['relative'] = self.__relative__(other)
        else:
            raise TypeError('Unable to add unknown type to path (%s)' % type(other))
        return type(self)(resdict)
    
    def __radd__(self, other):
        if 'header' in self:
            raise TypeError('Unable to add more path before header')
        resdict = {}
        resdict.update(self)
        if Grimoire.Utils.isInstance(other, types.BaseStringType):
            other = type(self)(other)
        if Grimoire.Utils.isInstance(other, type(self)):
            if 'trailer' in other:
                raise TypeError('Unable to add more path after trailer')
            if 'header' in other:
                resdict['header'] = other['header']
            if 'relative' in other:
                if 'relative' in resdict:
                    resdict['relative'] = other['relative'] + resdict['relative']
                else:
                    resdict['relative'] = other['relative']
        elif Grimoire.Utils.isInstance(other, types.ListType, types.TupleType):
            if 'relative' in resdict:
                resdict['relative'] = other + resdict['relative']
            else:
                resdict['relative'] = self.__relative__(other)
        else:
            raise TypeError('Unable to add unknown type to path (%s)' % type(other))
        return type(self)(resdict)

    def __len__(self):
        return len(self['relative'])

    def __calcslice__(self, index):
        start, end = index.start, index.stop

        ln = len(self)
        
        if start is None:
            start = 0
        elif start < 0:
            start += ln

        if end is None:
            end = ln
        elif end < 0:
            end += ln

        if start > ln:
            start = ln
        if end > ln:
            end = ln

        if start > end:
            raise TypeError("Start > end may not be used with Paths")

        return start, end, ln


    def __getitem__(self, index, exclude = 0):
        if isinstance(index, types.BaseStringType):
            return types.DictType.__getitem__(self, index)
        elif not isinstance(index, types.SliceType):
            return self['relative'][index]

        start, end, ln = self.__calcslice__(index)

        resdict = {}
        if start == 0 and exclude != -1 and 'header' in self:
            resdict['header'] = self['header']
        resdict['relative'] = self['relative'][start:end]
        if end == ln and exclude != 1 and 'trailer' in self:
            resdict['trailer'] = self['trailer']
        return type(self)(resdict)

    def __setitem__(self, index, value):
        if isinstance(index, types.BaseStringType):
            types.DictType.__setitem__(self, index, value)
            return
        elif not isinstance(index, types.SliceType):
            self['relative'][index] = value
            return

        start, end, ln = self.__calcslice__(index)

        newself = self.__getitem__(slice(None, start), 1) + value + self.__getitem__(slice(end, None), -1)

        if 'header' in self: del self['header']
        if 'relative' in self: del self['relative']
        if 'trailer' in self: del self['trailer']
        self.update(newself)
        
    def __delitem__(self, index):
        if isinstance(index, types.BaseStringType):
            types.DictType.__delitem__(self, index)
            return
        elif not isinstance(index, types.SliceType):
            del self['relative'][index]
            return

        start, end, ln = self.__calcslice__(index)

        newself = self.__getitem__(slice(None, start), 1) + self.__getitem__(slice(end, None), -1)

        if 'header' in self: del self['header']
        if 'relative' in self: del self['relative']
        if 'trailer' in self: del self['trailer']
        self.update(newself)
    

class Relative(Representation.RepresentationSequence, AbstractPath): pass

class InfoSetAbstractPath(types.DictType, AbstractPath): pass

class URIHeader(InfoSetAbstractPath):
    def __parse__(cls, str):
        resdict = {}
        if str and str.find('://') != -1:
            resdict['method'], str = str.split('://')
            source = str
            str = ''
            if source.find('/') != -1:
                source, str = source.split('/', 1)
            if source:
                resdict['source'] = source
                if resdict['source'] and resdict['source'].find('@') != -1:
                    (resdict['user'], resdict['source']) = resdict['source'].split('@')
                    if resdict['user'].find(':') != -1:
                        (resdict['user'], resdict['pwd']) = resdict['user'].split(':')
                if resdict['source'] and resdict['source'].find(':') != -1:
                    (resdict['source'], resdict['port']) = resdict['source'].split(':', 1)
        elif str.startswith('/'):
            str = str[1:]
        else:
            raise NoPartError
        return cls(resdict), str

class URIRelative(Relative):
    delimiter = '/'
    def __parse__(cls, str):
        paramstr = ''
        if '?' in str:
            str, paramstr = str.split('?')
        res, str = super(URIRelative, cls).__parse__(str)
        return res, str + paramstr

class URIParameters(InfoSetAbstractPath):
    def __parse__(cls, str):
        if not str:
            raise NoPartError
        return cls(dict([namevalue.split('=') for namevalue in str.split('&')])), ''

class URI(PathCombination):
    __header__ = URIHeader
    __relative__ = URIRelative
    __trailer__ = URIParameters


class LocalHeader(InfoSetAbstractPath):
    partNames = ('method', 'source')
    def __parse__(cls, str):
        method = 'file'
        source = None
        if hasattr(os.path, 'expanduser'):
            str = os.path.expanduser(str)
        if hasattr(os.path, 'normcase'):
            str = os.path.normcase(str)
        if hasattr(os.path, 'splitunc'):
            source, str = os.path.splitunc(str)
            method = 'unc'
        if not source and hasattr(os.path, 'splitdrive'):
            source, str = os.path.splitdrive(str)
        if not source:
            if os.sep and str.startswith(os.sep):
                str = str[len(os.sep):]
                source = os.sep
            elif os.altsep and str.startswith(os.altsep):
                str = str[len(os.altsep):]
                source = os.altsep
        if not source:
            raise NoPartError
        return cls({'source': source, 'method': method}), str

class LocalRelative(Relative):
    delimiter = os.sep
    def __parse__(cls, str):
        path = []
        first = True
        while first:
            str, first = os.path.split(str)
            if first:
                path[0:0] = [first]
        return cls(path), str

class LocalTrailer(AbstractPath):
    def __parse__(cls, str):
        raise NoPartError

class LocalPath(PathCombination):
    __header__ = LocalHeader
    __relative__ = LocalRelative
    __trailer__ = LocalTrailer


defaultLocalRoot = LocalPath(os.sep)

protocolMapping = {'dirt':('dirt', 8445),
                   'ssl.dirt': ('ssl.dirt', 8446)}

def canonizeURI(uri):
    method = uri.method.lower()
    if method in protocolMapping:
        if not uri.parts[0].port:
            uri.parts[0].port = protocolMapping[uri.method.lower()][1]
        uri.parts[0].method = protocolMapping[uri.method.lower()][0]
