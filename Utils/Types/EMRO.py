from Grimoire.Utils import Obj
from Grimoire.Utils.Types import Iter
import types

class EMROMethod(object):
    def __init__(self, preFns = [], postFns = []):
        self.preFns = preFns
        self.postFns = postFns

class EMROType(types.TypeType):
    def __new__(cls, name, bases, dict):
        emroMethods = {}
        if '__emroMethods__' in dict:
            emroMethods = dict['__emroMethods__']
        for key, value in dict.iteritems():
            if Obj.isInstance(value, EMROMethod):
                if key not in emroMethods:
                    emroMethods[key] = ([], [])
                emroMethods[key][0].extend(value.preFns)
                emroMethods[key][1].extend(value.postFns)
        dict['__emroMethods__'] = emroMethods

        def toRecursiveFn(fn):
            def EMROMethod(*arg, **kw):
                return fn(EMROMethod, *arg, **kw)
            return EMROMethod
        for key in dict['__emroMethods__'].iterkeys():
            dict['__emroMethods__'][key] = ([toRecursiveFn(method)
                                             for method in dict['__emroMethods__'][key][0]],
                                            [toRecursiveFn(method)
                                             for method in dict['__emroMethods__'][key][1]])

        obj = types.TypeType.__new__(cls, name, bases, dict)
        items = Iter.Reverse(bases) + [obj]
        emroMethods = {}
        for item in items:
            if hasattr(item, '__emroMethods__'):
                for key in item.__emroMethods__.iterkeys():
                    emroMethods[key] = ([], [])
        
        def merge(list1, list2):
            for item in list2:
                if item not in list1:
                    list1.append(item)
        for item in items:
            for key in emroMethods:
                if hasattr(item, '__emroMethods__') and key in item.__emroMethods__:
                    merge(emroMethods[key][0], item.__emroMethods__[key][0])
                    merge(emroMethods[key][1], item.__emroMethods__[key][1])
                elif hasattr(item, key):
                    merge(emroMethods[key][1], [getattr(item, key)])
        obj.__emroMethods__ = emroMethods

        for key in emroMethods:
            if emroMethods[key][0]:
                setattr(obj, key, emroMethods[key][0][0])
            else:
                setattr(obj, key, emroMethods[key][1][-1])

        return obj

    def __super__(cls, name, selffn, self):
        # We want __getattribute__ to be able to use emro without causing infinite recursion.
        methods = object.__getattribute__(self, '__class__').__emroMethods__[name]
        try:
            res = methods[0][methods[0].index(selffn) + 1]
        except IndexError:
            res = methods[1][-1]
        except ValueError:
            res = methods[1][methods[1].index(selffn) - 1]
        return types.MethodType(res, self, cls)

    def __add_emro__(cls, name):
        if not hasattr(cls, '__emroMethods__'):
            cls.__emroMethods__ = {}
        if name not in cls.__emroMethods__:
            cls.__emroMethods__[name] = ([], [])        
    __add_emro__ = classmethod(__add_emro__)

    def __add_pre__(cls, name, fn):
        cls.__add_emro__(name)
        cls.__emroMethods__[name][0] = fn
    __add_pre__ = classmethod
    
    def __add_pre__(cls, name, fn):
        cls.__add_emro__(name)
        cls.__emroMethods__[name][1] = fn

class EMRO(object):
    __metaclass__ = EMROType
    __emroMethods__ = {}
