class GenericIter:
    def __iter__(self):
        return self

class NormalizedIter:
    iterClass = None
    def __init__(self, *arg, **kw):
        self.expanded = None
        self.itered =  False
        self.arg = arg
        self.kw = kw

    def __iter__(self):
        if self.expanded is None:
            self.itered = True
            return self.iterClass(*self.arg, **self.kw)
        return iter(self.expanded)

    def __expand(self):
        if self.expanded is None:
            if self.itered:
                raise AttributeError
            expanded = []
            for item in self:
                expanded += [item]
            self.expanded = expanded        

    def __getattr__(self, name):
        self.__expand()
        try:
            return getattr(self.expanded, name)
        except AttributeError, e:
            if not name.startswith('__r'):
                raise e
            def rop(other):
                return getattr(other, '__' + name[3:])(self.expanded)
            return rop

    # FIXME: Fix getslice to support [x:y] efficiently...

class FilterOutError(Exception):
    pass

class MapIter(GenericIter):
    def __init__(self, function, *iters):
        self.function = function
        self.single = (len(iters) == 1)
        if self.single:
            self.iter = iters[0]
        else:
            self.iter = Zip(*iters)
        self.iter = iter(self.iter)
    def next(self):
        for item in self.iter:
            try:
                if self.single:
                    return self.function(item)
                else:
                    return self.function(*item)
            except FilterOutError:
                pass
        raise StopIteration()

class Map(NormalizedIter):
    iterClass = MapIter

class PrefixesSuffixesIter(GenericIter):
    def __init__(self, lst):
        self.lst = lst
        self.pos = len(lst)
    def next(self):
        if self.pos < 0:
            raise StopIteration()
        res = (self.lst[:self.pos], self.lst[self.pos:])
        self.pos -= 1
        return res

class PrefixesSuffixes(NormalizedIter):
    iterClass = PrefixesSuffixesIter

def Prefixes(lst):
    return Map(lambda (prefix, suffix): prefix, PrefixesSuffixes(lst))

def Suffixes(lst):
    return Map(lambda (prefix, suffix): suffix, PrefixesSuffixes(lst))

class EachIter(GenericIter):
    def __init__(self, lst, pos):
        self.lst = lst
        self.len = len(lst)
        self.pos = pos
        self.curPos = 0
    def next(self):
        while self.curPos % self.pos != 0:
            self.curPos += 1
        if self.curPos >= self.len:
            raise StopIteration()
        res = self.lst[self.curPos]
        self.curPos += 1
        return res

class Each(NormalizedIter):
    iterClass = EachIter

class ZipIter(GenericIter):
    def __init__(self, *lsts):
        self.lsts = map(iter, lsts)
    def next(self):
        return tuple(map(lambda x: x.next(), self.lsts))

class Zip(NormalizedIter):
    iterClass = ZipIter

class ReverseIter(GenericIter):
    def __init__(self, lst):
        self.pos = -1
        self.lst = list(lst)
    def next(self):
        try:
            res = self.lst[self.pos]
        except IndexError:
            raise StopIteration()
        self.pos -= 1
        return res

class Reverse(NormalizedIter):
    iterClass = ReverseIter

def Lump(lst, factor):
    return Zip(* Map(lambda n: Each(lst[n:], factor),
                     xrange(0, factor)))

class FlattenIter(GenericIter):
    def __init__(self, lst):
        self.lst = iter(lst)
        self.curItem = None
    def next(self):
        if self.curItem:
            for item in self.curItem:
                return item
        item = self.lst.next()
        try:
            self.curItem = iter(item)
            return self.next()
        except TypeError:
            return item

class Flatten(NormalizedIter):
    iterClass = FlattenIter
