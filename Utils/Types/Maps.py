from Grimoire.Utils import Obj
from Grimoire.Utils.Types import Wrapper
from Grimoire.Utils.Types import SortedList
from Grimoire.Utils.Types import Iter
import types, weakref, traceback

class ModifyGeneralizedDictMixIn(types.DictType):
    __slots__ = []
    def __init__(self, *arg, **kw):
        super(ModifyGeneralizedDictMixIn, self).__init__()
        if arg:
            self.update(arg[0])
        if kw:
            self.update(kw)
    
    def update(self, dict):
        for key, value in dict.iteritems():
            self[key] = value

    def clear(self):
        for key, value in self.iterkeys():
            del self[key]

    def pop(self, key, *arg):
        if arg:
            try:
                res = self[key]
                del self[key]
                return res
            except:
                return arg[0]
        res = self[key]
        del self[key]
        return res

    def popitem(self):
        for item in self.iteritems():
            del self[item[0]]
            return item
        raise KeyError
    
    def setdefault(key, default = None):
        if key not in self:
            self[key] = default
        return self[key]        

class UseGeneralizedDictMixIn(types.DictType):
    __slots__ = []
    def __contains__(self, name):
        try:
            self[name]
            return True
        except KeyError:
            return False

    def __iter__(self):
        return self.iterkeys()

    def get(self, key, default=None):
        try:
            return self[key]
        except:
            return default

    def has_key(self, key):
        return key in self

    def keys(self):
        return list(self.iterkeys())

    def values(self):
        return list(self.itervalues())

    def items(self):
        return list(self.iteritems())

class IterGeneralizedDictMixIn(UseGeneralizedDictMixIn):
    __slots__ = []
    def iterkeys(self):
        for (key, value) in self.iteritems():
            yield key

class CopyGeneralizedDictMixIn(types.DictType):
    __slots__ = []
    def copy(self):
        res = self.__class__()
        res.update(self)
        return res

    def fromkeys(cls, *arg):
        res = cls()
        res.update(types.DictType.fromkeys(*arg))
        return res
    fromkeys = classmethod(fromkeys)

class ImmutableMappingMixIn(ModifyGeneralizedDictMixIn):
    __slots__ = ['__immutable__']
    def __init__(self, *arg, **kw):
        self.__immutable__ = False
        super(ImmutableMappingMixIn, self).__init__(*arg, **kw)
        self.__immutable__ = True
    def __setitem__(self, name, value):
        if self.__immutable__:
            raise TypeError("Object is immutable")
        super(ImmutableMappingMixIn, self).__setitem__(name, value)
    def __delitem__(self, name):
        if self.__immutable__:
            raise TypeError("Object is immutable")
        super(ImmutableMappingMixIn, self).__delitem__(name)
    def __hash__(self):
        return id(self)

class AddableMappingMixIn(types.DictType):
    __slots__ = []
    def __add__(self, other):
        newValue = self.__class__()
        newValue.update(self)
        newValue.update(other)
        return newValue

    def __radd__(self, other):
        newValue = self.__class__()
        newValue.update(other)
        newValue.update(self)
        return newValue

class OrderedMappingMixIn(ModifyGeneralizedDictMixIn, IterGeneralizedDictMixIn):
    __slots__ = ['__keys__']
    def __insert_order__(self, name):
        self.__keys__.append(name)

    def __setitem__(self, name, value):
        if name not in self.__keys__:
            self.__insert_order__(name)
        super(OrderedMappingMixIn, self).__setitem__(name, value)

    def __delitem__(self, name):
        super(OrderedMappingMixIn, self).__delitem__(name)
        self.__keys__.remove(name)

    def __asymetric_getitem__(self, name):
        return types.DictType.__getitem__(self, name)
        
    def iteritems(self):
        return Iter.Map(lambda key: (key, self.__asymetric_getitem__(key)), self.__keys__)

class ImmutableMapping(ImmutableMappingMixIn, types.DictType):
    __slots__ = ['__weakref__']

class OrderedMapping(OrderedMappingMixIn, types.DictType):
    __slots__ = ['__weakref__']
    def __init__(self, *arg, **kw):
        self.__keys__ = []
        super(OrderedMapping, self).__init__(*arg, **kw)
        
class MapWrapper(ModifyGeneralizedDictMixIn, CopyGeneralizedDictMixIn,
                 IterGeneralizedDictMixIn, AddableMappingMixIn,
                 types.DictType):
    __slots__ = ['__weakref__']

class AnyMapKey(object):
    __slots__ = ['key', 'hash', '__weakref__']
    def __init__(self, key):
        self.key = key
        self.hash = Obj.hashAnyNonHashable(self.key)
    def __hash__(self):
        return self.hash
    def __cmp__(self, other):
        return cmp(self.key, other.key)
    def __repr__(self):
        return "<AnyMapKey " + repr(self.key) + ">"
    def __str__(self):
        return "<AnyMapKey " + str(self.key) + ">"
    def __unicode__(self):
        return "<AnyMapKey " + unicode(self.key) + ">"

class AnyMap(MapWrapper):
    __slots__ = []
    def __anykey__(self, name):
        try:
            hash(name)
            return name
        except:
            return AnyMapKey(name)
    def __getitem__(self, name):
        return super(AnyMap, self).__getitem__(self.__anykey__(name))
    def __setitem__(self, name, value):
        return super(AnyMap, self).__setitem__(self.__anykey__(name), value)
    def __delitem__(self, name):
        super(AnyMap, self).__delitem__(self.__anykey__(name))
    def iteritems(self):
        def filter((key, value)):
            if isinstance(key, AnyMapKey):
                key = key.key
            return (key, value)
        return Iter.Map(filter,
                        super(AnyMap, self).iteritems())

class AnyDescendantType(object):
    __slots__ = []
    def __isInstance__(self, obj):
        return True
    def __isInstanceOf__(self, obj):
        return obj is self
    def __isSubclassOf__(self, obj):
        return obj is self
    def __isSubclass__(self, obj):
        return True
    def __reprs__(self):
        return "<any descendant of " + repr(self.key) + ">"
    def __str__(self):
        return "<any descendant of " + str(self.key) + ">"
    def __unicode__(self):
        return "<any descendant of " + unicode(self.key) + ">"
AnyDescendant = AnyDescendantType()

class SubTypeMap(MapWrapper, OrderedMappingMixIn):
    __slots__ = []
    def __init__(self, *arg, **kw):
        self.__keys__ = SortedList.SortedList([], Obj.subtypeCmp)
        super(SubTypeMap, self).__init__(*arg, **kw)

    def __getitem__(self, name):
        p = self.__keys__.pos(name)
        if p < len(self.__keys__):
            for key in self.__keys__[p:]:
                if Obj.isSubclass(name, key):
                    return super(SubTypeMap, self).__getitem__(key)
        raise KeyError(name, self)
    
    def __insert_order__(self, name):
        self.__keys__.insertSort(name)

class InstanceMap(SubTypeMap):
    __slots__ = []
    def __getitem__(self, name):
        p = self.__keys__.pos(Obj.classOfInstance(name))
        if p < len(self.__keys__):
            for key in self.__keys__[p:]:
                if Obj.isInstance(name, key):
                    return super(SubTypeMap, self).__getitem__(key)
        raise AttributeError(name)

class DescMap(SubTypeMap):
    __slots__ = []
    def __getitem__(self, name):
        try:
            return super(DescMap, self).__getitem__(name)
        except AttributeError:
            pass
        except KeyError:
            pass
        if type(name) == types.InstanceType:
            try:
                return super(DescMap, self).__getitem__(Obj.classOfInstance(name))
            except AttributeError:
                pass
            except KeyError:
                pass
        try:
            return super(DescMap, self).__getitem__(type(name))
        except AttributeError:
            pass
        except KeyError:
            pass
        raise KeyError(name, self)

class InMap(MapWrapper):
    __slots__ = []
    def __getitem__(self, key):
        if types.DictType.__contains__(self, key):
            return super(InMap, self).__getitem__(key)
        for mapkey, mapvalue in self.iteritems():
            try:
                if key in mapkey:
                    return super(InMap, self).__getitem__(mapkey)
            except TypeError:
                pass
        raise KeyError(key, self)

class WeakKeyMap(MapWrapper, IterGeneralizedDictMixIn):
    """Mapping class that references keys weakly.

    Entries in the dictionary will be discarded when there is no
    longer a strong reference to the key. This can be used to
    associate additional data with an object owned by other parts of
    an application without adding attributes to those objects. This
    can be especially useful with objects that override attribute
    accesses."""
    __slots__ = ['_remove']
    def __init__(self, *arg, **kw):
        super(WeakKeyMap, self).__init__(*arg, **kw)
        def remove(key, selfref=weakref.ref(self)):
            self = selfref()
            if self is not None:
                super(WeakKeyMap, self).__delitem__(key)
        self._remove = remove
    def __weakref__(self, *arg, **kw):
        return weakref.ref(*arg, **kw)
    def __getitem__(self, name):
        return super(WeakKeyMap, self).__getitem__(self.__weakref__(name))
    def __setitem__(self, name, value):
        super(WeakKeyMap, self).__setitem__(self.__weakref__(name, self._remove), value)
    def __delitem__(self, name):
        super(WeakKeyMap, self).__delitem__(self.__weakref__(name))
    def iteritems(self):
        return Iter.Map(lambda (key, value): (key(), value),
                        super(WeakKeyMap, self).iteritems())

class AnyWeakKeyMapRemove(object):
    __slots__ = ['map', 'key']
    def __init__(self, map, key):
        self.map = weakref.ref(map)
        self.key = weakref.ref(key)
    def __call__(self, *arg, **kw):
        map = self.map()
        key = self.key()
        if map and key:
            super(AnyWeakKeyMap, map).__delitem__(key)

class AnyWeakKeyMap(MapWrapper):
    """This is like a mix between WeakKeyMap and AnyMap - any keys are
    allowed, and those that support weak references only have weak
    references to them added to this mapping.

    Unfourtunately, this mapping can not inherit from WeakKeyMap and
    AnyMap due to limitations in the ReferenceType implementation - it
    is impossible to inherit from it."""
    __slots__ = ['_remove']
    def __init__(self, *arg, **kw):
        super(AnyWeakKeyMap, self).__init__(*arg, **kw)
        def remove(key, selfref=weakref.ref(self)):
            self = selfref()
            if self is not None:
                super(AnyWeakKeyMap, self).__delitem__(key)
        self._remove = remove
    def __weakref__(self, value, *arg, **kw):
        try:
            return weakref.ref(value, *arg, **kw)
        except:
            return value
    def __anykey__(self, name):
        try:
            hash(name)
            return self.__weakref__(name)
        except:
            return AnyMapKey(self.__weakref__(name))
    def __getitem__(self, name):
        return types.DictType.__getitem__(self, self.__anykey__(name))
    def __setitem__(self, name, value):
        try:
            hash(name)
            key = self.__weakref__(name, self._remove)
        except:
            key = AnyMapKey.__new__(AnyMapKey)
            remove = AnyWeakKeyMapRemove(self, key)
            key.__init__(self.__weakref__(name, remove))
        return types.DictType.__setitem__(self, key, value)
    def __delitem__(self, name):
        types.DictType.__delitem__(self, self.__anykey__(name))
    def iteritems(self):
        def filter((key, value)):
            if isinstance(key, AnyMapKey):
                key = key.key
            if isinstance(key, types.ReferenceType):
                return (key(), value)
            return (key, value)
        return Iter.Map(filter,
                        types.DictType.iteritems(self))
