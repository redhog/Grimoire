from Grimoire.Utils.Types import Iter


def isPrefix(prefix, list):
    prefixLen = len(prefix)
    return prefixLen <= len(list) and prefix == list[:prefixLen]

def removePrefix(prefix, list):
    prefixLen = len(prefix)
    if prefixLen > len(list) or prefix != list[:prefixLen]:
        raise Iter.FilterOutError
    return list[prefixLen:]

def whichPrefix(l1, l2):
    l1len = len(l1)
    l2len = len(l2)
    plen = min(l1len, l2len)
    if l1[:plen] == l2[:plen]:
        return cmp(l1len, l2len)
    return None

def commonPrefix(l1, l2):
    for index in xrange(0, min(len(l1), len(l2))):
        if l1[index] != l2[index]:
            return l1[:index]
    return l1[:index + 1]        
    
def splitList(lst, sep, maxSplit = -1):
    res = [lst]
    splt = maxSplit
    while splt:
        try:
            index = res[-1].index(sep)
            res += [res[-1][index + 1:]]
            res[-2] = res[-2][:index]
        except ValueError:
            break;
        splt -= 1
    return res

def list2dict(lst):
    return dict(Iter.Lump(lst, 2))

def dict2list(dct):
    return Iter.Flatten(dct.items())
