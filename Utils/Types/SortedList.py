import types

class SortedList(types.ListType):
    __slots__ = ['cmpfunc']
    def __init__(self, value, cmpfunc = None, isSorted = 0, *arg, **kw):
        types.ListType.__init__(self, value, *arg, **kw)
        self.cmpfunc = cmpfunc or cmp
        if not isSorted:
            self.sort(self.cmpfunc)

    def index(self, x):
        ln = len(self)
        if ln:
            p = self.pos(x)
            if p != ln:
                if self.cmp(x, self[p]) == 0:
                    return p
        raise KeyError(x, self)

    def pos(self, x):
        "A normal binary search"
        ln = len(self)
        if ln == 0:
            return 0

        jump = pos = ln - 1

        while pos >= 0 and pos < ln:
            cmp = self.cmpfunc(x, self[pos])
            if cmp == 0:
                return pos
            elif jump <= 1:
                break
            jump /= 2
            pos += cmp * jump

        if cmp != 0:
            lastcmp = cmp
            while lastcmp == cmp:
                pos += cmp
                if not 0 <= pos < ln:
                    break
                lastcmp = self.cmpfunc(x, self[pos])
            if lastcmp == 1:
                pos += 1

        if pos < 0:
            return 0
        elif pos > ln:
            return ln

        return pos
    
    def insertSort(self, x):
        p = self.pos(x)
        self.insert(p, x)

    def __getslice__(self, i, j):
        i = max(i, 0); j = max(j, 0)
        return self.__class__(types.ListType.__getslice__(self, i, j), self.cmpfunc, 1)
