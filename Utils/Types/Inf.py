class InfinityClass(object):
    """Infinity is larger than any numerical value.
    """
    def __init__(self, isPositive):
        self.isPositive = isPositive
    def __add__(self, other):
        return self
    def __sub__(self, other):
        return self
    def __radd__(self, other):
        return self
    def __rsub__(self, other):
        if other is self:
            return other
        return infinities[not self.isPositive]
    def __cmp__(self, other):
        if other is self:
            return 0
        if self.isPositive:
            return 1
        return -1
    def __str__(self):
        return ['minus ', ''][self.isPositive] + 'infinity'
    def __unicode__(self):
        return unicode(str(self))
infinities = [InfinityClass(False), InfinityClass(True)]
minusInfinity = infinities[False]
infinity = infinities[True]
