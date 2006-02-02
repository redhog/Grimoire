import types, string

debugBases = 0

def convertToStrAnyWayPossible(obj):
    try:
        return unicode(obj)
    except Exception, e:
        try:
            return str(obj)
        except Exception, e2:
            return '{' + convertTypeToStrAnyWayPossible(obj) + ' @ ' + str(id(obj)) + ': ' +  objInfo(e) + '}'

def convertTypeToStrAnyWayPossible(obj):
    try:
        t = type(obj)
    except Exception, e:
        return '{' + objInfo(e) + '}'
    return objInfo(t)

def objInfo(obj):
    res = []
    t = type(obj)
    res += [convertToStrAnyWayPossible(obj)]
    if t == types.InstanceType or t == types.ClassType:
        klass = classOfInstance(obj)
        res += [objInfo(klass)]
    res += [convertToStrAnyWayPossible(t)]
    return '[' + string.join(res, ' ') + ']'

def getpath(obj, path):
    for part in path:
        obj = getattr(obj, part)
    return obj

def listClassAttr(klass):
    res = klass.__dict__.items()
    for parent in klass.__bases__:
        res += listClassAttr(parent)
    return res

def __classOfInstance(o):
    if type(o) is types.InstanceType:
        try:
            return o.__class__
        except:
            pass
    return type(o)

def bases(t, exc = True):
    """bases returns a list of base-classes for a class. This is
    similar to the __bases__ attribute, except objects and classes can
    override the mechanism using the method
    
    method       o.__baseClasses__(self) -> list of classes
    """
    if hasattr(__classOfInstance(t), '__baseClasses__'):
        try:
            return __classOfInstance(t).__baseClasses__(t)
        except Exception:
            pass
    try:
        return t.__bases__
    except Exception:
        pass
    if exc:
        if debugBases:
            raise AttributeError('Object ' + objInfo(t) + ' has no attribute __bases__')
        raise AttributeError
    return []

def isSubclass(t, *baseTypes):
    """isSubclass is similar to issubclass, except any object (for
    instance a type or an object) is considered a subclass of itself,
    and objects and classes can override the mechanisms for sublcass
    comparation using the methods

    method       t.__isSubclassOf__(b) -> boolean
    method       b.__isSubclass__(t) -> boolean
    
    If none of them is defined, isSubclass is equivalent to

    t is b or any of isSubclass(bt, b) for bt in bases(t)
    """
    def isSubclassOf(t, b):
        res = None
        classOfInstanceT = __classOfInstance(t)
        classOfInstanceB = __classOfInstance(b)
        if hasattr(classOfInstanceT, '__isSubclassOf__'):
            try:
                res = classOfInstanceT.__isSubclassOf__(t, b)
            except Exception:
                pass
        if not res and hasattr(classOfInstanceB, '__isSubclass__'):
            try:
                res = classOfInstanceB.__isSubclass__(b, t)
            except Exception:
                pass
        if res is not None:
            return res
        if t is b:
            return True
        try:
            for bt in bases(t):
                if isSubclassOf(bt, b):
                    return True
        except AttributeError:
            pass
        return False
    for b in baseTypes:
        if isSubclassOf(t, b):
            return True
    return False    

def classOfInstance(o):
    """classOfInstance returns the class it is an instance of. This is
    similar to the __class__ attribute, except objects and classes can
    override the mechanism using the methods

    method       o.__instanceOf__() -> list of classes
    """
    c = __classOfInstance(o)
    if not hasattr(c, '__instanceOf__'):
        return c
    try:
        return c.__instanceOf__(o)
    except Exception:
        return c

def isInstance(o, *ts):
    """isInstance is similar to isinstance, except objects and classes
    can override the mechanisms for sublcass comparation using the
    methods

    method       o.__isInstanceOf__(t) -> boolean
    method       t.__isInstance__(o) -> boolean

    If none of them is defined, isInstance is equivalent to
    
    isSubclass(classOfInstance(o), *ts)
    """
    def isInstanceOf(o, t):
        res = None
        classOfInstance = __classOfInstance(o)
        if hasattr(classOfInstance, '__isInstanceOf__'):
            try:
                res = classOfInstance.__isInstanceOf__(o, t)
            except:
                pass
        classOfType = __classOfInstance(t)
        if hasattr(classOfType, '__isInstance__'):
            try:
                res = res or classOfType.__isInstance__(t, o)
            except:
                pass
        if res is not None:
            return res
        try:
            return isSubclass(classOfInstance, *ts)
        except AttributeError:
            return 0
    for t in ts:
        if isInstanceOf(o, t):
            return 1
    return 0

def isDescendant(o, *baseTypes):
    return isSubclass(o, *baseTypes) or isInstance(o, *baseTypes)

def commonParentClass(*o):
    def common2ParentClass(o1, o2):
        if isSubclass(o2, o1):
            return o1
        for base in bases(o1):
            try:
                return common2ParentClass(base, o2)
            except NameError:
                pass
        raise NameError
    if len(o) == 1:
        return o[0]
    return commonParentClass(common2ParentClass(o[0], o[1]), *o[2:])

def instanceCommonParentClass(o1, o2):
    return commonParentClass(classOfInstance(o1),
                             classOfInstance(o2))

def mergeClasses(klasses):
    singleklasses = []
    for klass in klasses:
        exchanged = False
        for index in xrange(0, len(singleklasses)):
            if isSubclass(klass, singleklasses[index]):
                singleklasses[index] = klass
                exchanged = True
            elif isSubclass(singleklasses[index], klass):
                exchanged = True
        if not exchanged:
            singleklasses.append(klass)

    if len(singleklasses) == 1:
        return singleklasses[0]

    metaklasses = [classOfInstance(klass) for klass in singleklasses]
    metaklass = mergeClasses(metaklasses)

    return types.TypeType.__new__(
        metaklass,
        'Merge' + str(singleklasses),
        tuple(singleklasses), {})

def subtypeCmp(x, y):
    """Compares classes from a strict inheritance _tree_ or set of
    trees, according to a total ordering of said tree. Ancestors are
    considered greater than their childrens. Two classes with a common
    parent are compared according to their Python object ID. Two
    classes with a common ancestor are compared according to their
    ancestors that are direct childrens of the common one. Classes
    with no common ancestor are compared according to the Python
    object ID of their greatest ancestors.
    """
    if x is y:
        return 0
    elif isSubclass(y, x):
        return 1
    elif isSubclass(x, y):
        return -1
    else:
        # FIXME: What if x and y have a common ancestor, but inherits
        # from other (non-common) classes too, and have those classes
        # first in their inheritance lists?
        oldx = x # Not strictly needed...
        bx = bases(x, False)
        while bx and not isSubclass(y, x):
            oldx = x
            x = bx[0]
            bx = bases(x, False)
        oldy = y
        if y != x:
            by = bases(y, False)
            while by and y != x:
                oldy = y
                y = by[0]
                by = bases(y, False)
        if isSubclass(oldy, x):
            x = oldx
            y = oldy
        return cmp(id(x), id(y))

def hashAny(obj):
    try:
        return hash(obj)
    except TypeError:
        pass
    if isinstance(obj, types.ListType):
        res = 3430009 # 3430009 == hash(()) + 1
        for v in obj:
            res += hashAny(v)
        return hash(res)
    elif isinstance(obj, types.ReferenceType):
        return hashAny(obj())
    return id(obj)

def hashAnyNonHashable(obj):
    if isinstance(obj, types.ListType):
        res = 3430009 # 3430009 == hash(()) + 1
        for v in obj:
            res += hashAny(v)
        return hash(res)
    elif isinstance(obj, types.ReferenceType):
        return hashAnyNonHashable(obj())
    return id(obj)
