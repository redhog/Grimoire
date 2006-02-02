from Grimoire.Utils.Types import Wrapper as TypesWrapper
from Grimoire.Utils.Types import Maps as TypesMaps
import types, weakref, sys


def Curry(obj, *objarg, **objkw):
    def curryfn(fn, arg, kw):
        callkw = {}
        callkw.update(objkw)
        callkw.update(kw)
        return fn(*(objarg + arg), **callkw)
    if isinstance(obj, (types.TypeType, types.ClassType)):
        class res(obj):
            def __init__(self, *arg, **kw):
                return curryfn(obj.__init__, (self,) + arg, kw)
    else:
        def res(*arg, **kw):
            return curryfn(obj, arg, kw)
    return res

cachingFunctionCache = TypesMaps.AnyWeakKeyMap()

class cachingFunctionCacheKwsDelimiter: pass
class cachingFunctionCacheValue: pass

def cachingFunctionCacheGet(fn, *args, **kws):
    node = cachingFunctionCache
    
    try:
        node = node[fn]
    except:
        newNode = TypesMaps.AnyWeakKeyMap()
        node[fn] = newNode
        node = newNode

    for nodeKey in args:
        try:
            node = node[nodeKey]
        except:
            newNode = TypesMaps.AnyWeakKeyMap()
            node[nodeKey] = newNode
            node = newNode

    try:
        node = node[cachingFunctionCacheKwsDelimiter]
    except:
        newNode = TypesMaps.AnyWeakKeyMap()
        node[cachingFunctionCacheKwsDelimiter] = newNode
        node = newNode

    if kws:
        keys = kws.keys()
        keys.sort()
        for key in keys:
            nodeKey = kws[key]
            try:
                node = node[nodeKey]
            except:
                newNode = TypesMaps.AnyWeakKeyMap()
                node[nodeKey] = newNode
                node = newNode

    try:
        result = node[cachingFunctionCacheValue]
    except:
        try:
            result = (1, fn(*args, **kws))
        except:
            result = (0, sys.exc_info())
        node[cachingFunctionCacheValue] = result
    if result[0]:
        return result[1]
    raise result[1][0], result[1][1], result[1][2]

def cachingFunction(fn):
    def cachingFunction(*arg, **kw):
        return cachingFunctionCacheGet(fn, *arg, **kw)
    return cachingFunction
