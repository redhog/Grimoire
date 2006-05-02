"""
The Performer module is used to control access to user-defined
classes. External access to the methods of the user-class is
controlled by abilities, as specified in the ability-module.
"""

import operator, string, types, sys, Grimoire.Types, Grimoire.Types.Ability, Grimoire.Utils, Grimoire.Utils.RPC, traceback


debugMethodNotImplementedHere = 0
debugTreeOps = ('dir', 'related')


UnlimitedDepth = Grimoire.Utils.InfinityClass(True)
MethodBaseDepth = Grimoire.Utils.InfinityClass(True)

def DirListFilter(prefix, depth, listing, chop=True, pathPos=1):
    """Filters a list of tuples. In each tuple, the first element must
    signify "leaf" status. Any other element might represent a path
    (default is second element). Entries with a path that begins with
    prefix, are included in the output, with that prefix removed from
    the path of the entries. In addition, if the remaining path is
    longer than depth, the entry is removed from the output if chop is
    False, and truncated to depth otherwize. If path is truncated, the
    "leaf" status is automatically set to 0."""    
    prefixLen = len(prefix)
    depth = depth + prefixLen
    def filterFn(entry):
        entry = list(entry) # Copy entry and make it a list
        if not Grimoire.Utils.isPrefix(prefix, entry[pathPos]):
            raise Grimoire.Utils.FilterOutError()
        end = len(entry[pathPos])
        if depth < end:
            if not chop:
                raise Grimoire.Utils.FilterOutError()
            entry[0] = 0
            end = depth
        entry[pathPos] = entry[pathPos][prefixLen:end]
        return tuple(entry)
    return Grimoire.Utils.Map(filterFn, listing)

def DirListExtender(prefix, depth, dirlistfn, extendfn, onlyFullPaths = True):
    """Extends one dirlisting with another. It is easies to explain if
    one disregards prefix and depth (or sets prefix=[] and
    depth=Unlimited), then, this is what happends:

    Grimoire.Utils.Flatten([[(leaf2, path + path2)
                             for (leaf2, path2) in extendfn((leaf, path))]
                            for (leaf, path) in dirlistfn()])
    """

    realprefix = prefix[:]
    realdepth = depth

    if onlyFullPaths:
        depth = UnlimitedDepth
    
    # This finds the barrier between what part of the path dirlistfn
    # and extendfn is supposed to provide
    dirlist = list(dirlistfn(prefix, depth))
    while not dirlist and prefix:
        del prefix[-1]
        depth += 1
        dirlist = list(dirlistfn(prefix, depth))

    result = []
    for (leaf, path) in dirlist:
        path = prefix + path
        pathlen = len(path)
        subprefix = realprefix[pathlen:]
        subadd = path[len(realprefix):]
        subdepth = realdepth - max(pathlen - len(realprefix), 0)
        for (leaf2, path2) in extendfn((leaf, path), subprefix, subdepth):
            result.append((leaf2, subadd + path2))

    return result

# First of fns should be local implementation, rest may come from children.
def treeOp_combine_first_working(self, fns, **kw):
    for fn in fns:
        try:
            return fn(**kw)
        except:
            pass        
    raise sys.exc_type, sys.exc_value, sys.exc_traceback
def treeOp_combine_first(self, fns, **kw):
    for fn in fns:
        try:
            return fn(**kw)
        except Grimoire.Types.MethodNotImplementedHere:
            pass
    raise sys.exc_type, sys.exc_value, sys.exc_traceback
def treeOp_combine_most_specific_working(self, fns, **kw):
    res = None
    for fn in fns:
        try:
            tmpRes = fn(**kw)
            if not res or len(tmpRes['implementor']) > len(res['implementor']):
                res = tmpRes
        except:
            pass
    if res is not None:
        return res
    raise sys.exc_type, sys.exc_value, sys.exc_traceback
def treeOp_combine_all(self, fns, **kw):
    for fn in fns: fn(**kw)
    return {}
def treeOp_combine_append(self, fns, **kw):
    def apply(fn):
        try:
            return fn(**kw)['value']
        except Grimoire.Types.MethodNotImplementedHere:
            raise Grimoire.Utils.FilterOutError
    return {'value': Grimoire.Utils.Flatten(Grimoire.Utils.Map(apply, fns))}
def treeOp_combine_add(self, fns, **kw):
    def apply(fn):
        try:
            return fn(**kw)['value']
        except Grimoire.Types.MethodNotImplementedHere:
            raise Grimoire.Utils.FilterOutError
    return {'value': reduce(operator.add, Grimoire.Utils.Map(apply, fns), 0)}


class Performer(Grimoire.Utils.RPC.ServerObject):
    def __add__(self, other):
        if Grimoire.Utils.isInstance(other, Performer):
            return Composer(Physical(self), Physical(other))
        else:
            path = other
            if not Grimoire.Utils.isInstance(path, Grimoire.Types.GrimoireReference):
                path = Grimoire.Types.GrimoireReference(path)
            return Physical(self)._physicalGetpath(Grimoire.Types.CurrentNode, path['levels'], path['path'])
    def __radd__(self, path):
        return Prefixer(path, Physical(self))

class Logical(Performer):
    __slots__ = ['_physical']

    def __init__(self, physical):
        Performer.__init__(self)
        self._physical = Physical(physical)

    def __getattribute__(self, name):
        return Logical(Physical(self)._chunk([name]))

    def __call__(self, *arg, **kw):
        #### NOTE ###
        # If the next line moves, please change the number in the
        # debug-printout-filter in Physical._treeOp
        return Physical(self)._treeOp([], "call", callarg=arg, callkw=kw)

    def __add__(self, other):
        return Logical(super(Logical, self).__add__(other))

    def __radd__(self, other):
        return Logical(super(Logical, self).__radd__(other))

class Physical(Performer):
    """Physical is the base-class for all objects that makes up a
    Grimoire tree. It provides automatic cutting, as defined by the
    Cutter class.

    The "logical tree" is defined by, and operations on that tree are
    provided through, the _treeOp interface.
    """
    __slots__ = ['_fenceDistance', '_parent', '_root', '_base', '_baseLevel', '_dynamicPathForSelf']

    class __metaclass__(type(Performer)):
        def __call__(cls, *arg, **kw):
            if cls is Physical:
                def physical(obj):
                    if isinstance(obj, Logical):
                        return Performer.__getattribute__(obj, '_physical')
                    return obj
                return physical(*arg, **kw)
            return type(Performer).__call__(cls, *arg, **kw)

    def __init__(self):
        self._fenceDistance = Grimoire.Utils.ThreadLocalData(0)
        self._root = None
        self._dynamicPathForSelf = Grimoire.Utils.ThreadLocalStack()

    # Physical node API

    def _chunk(self, extrapath):
        return Cutter(self, extrapath)

    def _setParent(self, parent):
        self._parent = parent
        self._root = parent
        del self._fenceDistance # Not needed if not root, deleting it makes us catch some interresting bugs sometimes :)

    def _physicalParent(self):
        return self._parent

    def _physicalRoot(self):
        if not self._root:
            return self
        self._root = self._root._physicalRoot()
        return self._root

    def _callWithUnlockedTree(self, fn, *arg, **kw):
        root = self._physicalRoot()
        root._fenceDistance.set(root._fenceDistance + 1)
        try:
            return fn(*arg, **kw)
        finally:
            root._fenceDistance.set(root._fenceDistance - 1)

    def _unlockedTree(self):
        return self._physicalRoot()._fenceDistance > 0

    def _pathForChild(self, obj, extraPath = [], dynamic=False):
        """Returns the path for a child physical object in case this
        one is a container. For more information, see
        _pathForSelf()."""
        raise NotImplementedError

    def _pathForSelf(self, extraPath = [], dynamic=False):
        """Returns the path at which this physical is joined in the
        tree, as determined by any parent Prefixer:s. If dynamic is
        true however, it returns the actual path with which a treeOp
        was performed. This might differ when treevars are involved,
        as they might or might not be expanded in the dynamic case,
        but are never expanded in the static one."""
        if dynamic and self._dynamicPathForSelf:
            return self._dynamicPathForSelf.get() + extraPath
        try:
            return self._physicalParent()._pathForChild(self, extraPath, dynamic)
        except AttributeError:
            return extraPath

    def _setPhysicalBase(self, base):
        self._base = base

    def _physicalBase(self):
        return self._base
    
    def _setBaseLevel(self, level):
        self._baseLevel = level

    def _physicalGetpath(self, root = Grimoire.Types.CurrentNode, levels = 0, path = []):
        reslevels = levels
        if root is Grimoire.Types.TreeRoot:
            respath = []
        else:
            respath = self._pathForSelf()
            if root is Grimoire.Types.MethodBase:
                reslevels += self._baseLevel
        if reslevels:
            if len(respath) < reslevels:
                raise AttributeError('Too many parent levels for point in tree (parenting up past the root)')
            respath = respath[:-reslevels]
        respath = respath + path
        resobj = self._physicalRoot()
        if not respath:
            return resobj
        return Cutter(resobj, respath)

    def _reference(self, other):
        "Returns a GrimoireReference relative to this method, to another method (in the same tree)."
        other = Physical(other)
        if self._physicalRoot() is not other._physicalRoot():
            raise ValueError("Can not create references between methods of different trees")
        return Grimoire.Types.GrimoireReference(other._pathForSelf(dynamic=True), 0) - Grimoire.Types.GrimoireReference(self._pathForSelf(dynamic=True), 0)

    def _reReference(self, other, path):
        """Given a reference path relative another method object,
        return the same reference but relative the current method."""
        return Physical(other)._physicalGetpath(path) - self._pathForSelf(dynamic=True)

    def __description__(self, indentation):
        return indentation + self.__class__.__name__ + '\n'
    def __unicode__(self, indentation = ''):
        return self.__description__(indentation)
    def __str__(self):
        return str(self.__unicode__())

    # Physical -> Logical API
    # (methods that returns Logicals)

    def _getpath(self, *arg, **kw):
        return Logical(self._physicalGetpath(*arg, **kw))

    # Logical node API

    def _treeOp(self, path, treeOp, **kw):
        """Execute an operation named by treeOp (with argument *arg,
        **kw) on a node in the logical tree, specified by path.
        """
        if treeOp in debugTreeOps:
            tr = traceback.extract_stack()[:-1]
            if tr[-1][1] == 151:
                tr = tr[:-1]
            tr.reverse()
            def filter(item):
                prefix = Grimoire.__path__[0]
                if item[0].startswith(prefix):
                    return item[0][len(prefix):] + ':' + str(item[1])
                raise Grimoire.Utils.FilterOutError
            print "TreeOp:", ', '.join(Grimoire.Utils.Map(filter, tr))
            print "TreeOp:    -> " + treeOp + ': ' + '.'.join(self._pathForSelf(path)), kw
        try:
            return self._treeOp_recurse(path=path, treeOp=treeOp, wholePath=path, **kw)['value']
        except Grimoire.Types.MethodNotImplementedHere:
            if debugMethodNotImplementedHere: print "MethodNotImplementedHere:", self, path; traceback.print_exc()
            raise AttributeError(self._physicalRoot(), self._pathForSelf(path, True))

    def _treeOp_recurse(self, path, treeOp, **kw):
        """This method implements the varios operations that can be
        performed on this node."""
        raise Grimoire.Types.MethodNotImplementedHere(path)

    _treeOp_combine = treeOp_combine_first
    _treeOp_combine_count = treeOp_combine_add
    _treeOp_combine_call = treeOp_combine_first
    _treeOp_combine_params = treeOp_combine_first
    _treeOp_combine_dir = treeOp_combine_append
    _treeOp_combine_related = treeOp_combine_append
    _treeOp_combine_reload = treeOp_combine_all
    _treeOp_combine_implementor = treeOp_combine_first
    _treeOp_combine_translate = treeOp_combine_most_specific_working
    

class Handling(Physical):
    __slots__ = []
    def _treeOp_recurse(self, treeOp, **kw):
        return getattr(self, "_treeOp_handle_" +  treeOp,
                       self._treeOp_handle)(treeOp=treeOp, **kw)

    def _treeOp_handle(self, treeOp, **kw):
        raise Grimoire.Types.MethodNotImplementedHere(path)


class AbstractImplementing(Physical):
    __slots__ = []
    def _treeOp_impl(self, path, treeOp, **kw):
        raise Grimoire.Types.MethodNotImplementedHere(path)

    def _treeOp_impl_count(self, **kw):
        return {'value': 1}
    
    def _treeOp_impl_call(self, path, treeOp, callarg, callkw, **kw):
        raise Grimoire.Types.MethodNotImplementedHere(path)

    def _treeOp_impl_params(self, path, treeOp, **kw):
        """Used by introspection.params to inspect a method.

        The object returned should be a ParamsType object or an
        AnnotatedObject containing such an object.
        """
        
        raise Grimoire.Types.MethodNotImplementedHere(path)

    def _treeOp_impl_dir(self, path, treeOp, depth, **kw):
        """Used by introspection.dir to collect a directory listing.

        * The listing returned should be a list of pairs (leaf,
          localpath).
        * Pairs may be duplicated.
        * Paths should be rooted at the argument path (which is rooted
          at this physical node).
        * Paths longer than depth may be cut of to the length depth,
          and leaf set to 0 for them. For all other pairs, leaf should
          be 1.
        """
        return {'value': []}

    def _treeOp_impl_related(self, path, treeOp, depth, objectPath, objectDepth, **kw):
        """Used by introspection.relatedMethods to collect methods related to some object or method group.

        * The listing returned should be a list of quadrupples (leaf,
          objectPath, description, methodPath)
        * Quadrupples may be duplicated.
        * Method paths should be rooted at the argument path (which is
          rooted at this physical node).
        * Method paths longer than depth may be ommitted.
        * Object paths should be rooted at objectPath (which is rooted
          at The Root, i.e. is an absolute path).
        * Object paths longer than objectDepth may be cut of to the length
          depth, and leaf set to 0 for them. For all other pairs, leaf
          should be 1.
        """
        return {'value': []}

    def _treeOp_impl_reload(self, path, treeOp, **kw):
        return {}

    def _treeOp_impl_implementor(self, path, treeOp, **kw):
        raise Grimoire.Types.MethodNotImplementedHere(path)

    def _treeOp_impl_translate(self, path, treeOp, language, message, **kw):
        raise  Grimoire.Types.MethodNotImplementedHere(path)


class Implementing(AbstractImplementing):
    __slots__ = []
    def _treeOp_recurse(self, treeOp, **kw):
        return getattr(self, "_treeOp_impl_" +  treeOp,
                       self._treeOp_impl)(treeOp=treeOp, **kw)


class ImplementingHandling(AbstractImplementing, Handling):
    def _treeOp_handle(self, treeOp, **kw):
        return getattr(self, "_treeOp_impl_" +  treeOp,
                       self._treeOp_impl)(treeOp=treeOp, **kw)
    

class Cutter(Physical):
    """
    A Cutter cuts out a part of a Performer-object and presents it as a
    (new) Physical-object, namely all methods with a common prefix
    (basepath)."""
    __slots__ = ['_basepath']
    
    def __init__(self, performer, basepath = []):
        Physical.__init__(self)
        self._basepath = basepath
        Physical._setParent(self, Physical(performer))

    # Ugglyhacks

    # This is here to make sure that we won't lose the object we're
    # cutting if we get added to some other tree. This is really
    # uggly, and turning everything upside down and have the cutted
    # object as _child, inheriting from SingleChildContainer would
    # really be much better, if it didn't mean that
    # Physical(s.foo.bar)._physicalRoot() !=
    # Physical(s)._physicalRoot()
    
    def _setParent(self, parent):
        pass

    # Optimizations

    def _chunk(self, extrapath):
        return Cutter(self._physicalParent(), self._path(extrapath))

    # Physical node API

    def _performer(self):
        return self._physicalParent()

    def _path(self, extraPath = []):
        return self._basepath + extraPath

    def _pathForSelf(self, extraPath = [], dynamic=False):
        return self._physicalParent()._pathForSelf(self._path(extraPath), dynamic)

    def __unicode__(self, indentation = ''):
        return self.__description__(indentation) + self._physicalParent().__unicode__(indentation + ' ')

    # Logical node API

    def _treeOp_recurse(self, path, **kw):
        return self._physicalParent()._treeOp_recurse(path=self._path(path), **kw)

class Translation(Implementing):
    __slots__ = ['_translations']

    def __init__(self, translations):
        Implementing.__init__(self)
        self._translations = translations

    def _treeOp_impl_translate(self, path, treeOp, language, message, **kw):
        if not hasattr(self, '_translations'):
            raise Grimoire.Utils.UntranslatableError('No translation catalog set for this object')
        try:
            return {'value': self._translations([language]).ugettext(message), 'implementor': []}
        except AttributeError:
            raise Grimoire.Utils.UntranslatableError('No translation catalog set for this object')


class AbstractMethod(Implementing):
    __slots__ = []

    def _treeOp_recurse(self, path, treeOp, wholePath, **kw):
        self._dynamicPathForSelf.append(path and wholePath[:-len(path)] or wholePath)
        try:
            return Implementing._treeOp_recurse(self, path=path, treeOp=treeOp, wholePath=wholePath, **kw)
        finally:
            del self._dynamicPathForSelf[-1]

    def _treeOp_impl_related(self, path, depth, objectPath, objectDepth, **kw):
        return {'value': self._related(path, depth, objectPath, objectDepth)}

    # You may override these one in user classes if you whish to.

    __related_hasobjects__ = True
    
    def _related_group(self, path, depth, objectPath, objectDepth):
        if not hasattr(self, '__related_group__'): return None
        return self.__related_group__

    def _related_description(self, path, depth, objectPath, objectDepth):
        if hasattr(self, '__related_description__'): return self.__related_description__
        pathForSelf = self._pathForSelf()
        while pathForSelf and pathForSelf[-1].startswith('$'):
            del pathForSelf[-1]
        return pathForSelf

    def _related_objdir(self, path, depth):
        return self._treeOp(path, 'dir', depth=depth)

    def _related(self, path, depth, objectPath, objectDepth):
        """This magic attempts to do "the right thing" for you. In
        some cases it doesn't. Then you'l have to override it :) What
        it does is:
        
        Object paths returned are self.__related_group__ + treevars +
        path, where treevars are all $treevarnames at the end of the
        path to this method or sub method, and where path is just the
        ordinary path given to _call/_dir/_params in a submethod (and
        [] for a method).

        The description is either self.__related_description__ or if
        not set, the path to this method or sub method, with any
        terminating treevars removed.
        """
        
        relatedGroup = self._related_group(path, depth, objectPath, objectDepth)
        if relatedGroup is None: return []
        description = self._related_description(path, depth, objectPath, objectDepth)
        pathForSelf = self._pathForSelf()
        objPrefix = []
        while pathForSelf and pathForSelf[-1].startswith('$'):
            objPrefix[0:0] = [pathForSelf[-1]]
            del pathForSelf[-1]
        objPrefix, objPrefixLen, which = getPrefix(self,
                                                   objPrefix != [],
                                                   relatedGroup + objPrefix,
                                                   len(relatedGroup + objPrefix),
                                                   objectPath, True)
        objectPathLen = len(objectPath)
        addPath = []
        subPath = []
        if which == None:
            return []
        elif which == -1:
            addPath = objPrefix[objectPathLen:]
        elif which == 1:
            subPath = objectPath[objPrefixLen:]
        subObjDepth = objectDepth - max(0, (objPrefixLen - objectPathLen))
        if subObjDepth <= 0:
            if self.__related_hasobjects__:
                return [(0, [], description, subPath)]
            else:
                subObjDepth = 0            
        if depth is MethodBaseDepth:
            objlist = self._related_objdir(subPath, subObjDepth)
        else:
            objlist = self._treeOp(subPath, 'dir', depth=subObjDepth)
        return DirListFilter(path, depth,
                             Grimoire.Utils.Map(lambda (leaf, path): (leaf, addPath + path, description, subPath + path),
                                                objlist),
                             False, 3)


    def _treeOp_impl_implementor(self, path, **kw):
        if (1, []) in self._treeOp_recurse(path=path, treeOp='dir', depth=0, **kw)['value']:
            return self
        raise Grimoire.Types.MethodNotImplementedHere(path)

class Method(AbstractMethod):
    """A method is a leaf in a Grimoire tree. It represents a method
    that can be called on an object.

    Typically, you'd inherit this class, overiding at least _call and
    _params. _params should return an object of the type ParamsType
    (or an AnnotatedObject containing such an object).
    """
    __slots__ = []

    # Logical node API

    def _treeOp_recurse(self, path, **kw):
        if path: raise Grimoire.Types.MethodNotImplementedHere(path)
        return AbstractMethod._treeOp_recurse(self, path=path, **kw)

    def _treeOp_impl_call(self, path, callarg, callkw, **kw):
        return {'value': self._call(*callarg, **callkw)}

    def _treeOp_impl_params(self, **kw):
        return {'value': self._params()}

    def _treeOp_impl_dir(self, **kw):
        return {'value': [(1, [])]}

    # You may define this one in user classes if you whish to.

    # __related_group__ = ['some', 'object', 'path']
    # __related_description__ = ['some', 'descriptive', 'path']

    # User class API. Override these in a user-class

    def _call(self, *arg, **kw):
        raise NotImplementedError(self, '_call', *arg, **kw)

    def _params(self):
        raise NotImplementedError(self, '_params')

class SubMethod(AbstractMethod):
    """
    A SubMethod is a tree of methods. Given a SubMethod foo, calling
    foo.fie.bar.gazonk(*args, **kw) will result in a call
    foo._call(['fie', 'bar', 'gazonk'], *args, **kw).

    Note the differences in API from Method - all user functions takes
    a path as first (real) argument.
    """
    __slots__ = []
 
    # Logical node API

    def _treeOp_impl_call(self, path, callarg, callkw, **kw):
        if (1, []) not in self._treeOp_impl_dir(path=path, treeOp='dir', depth=0)['value']:
            raise Grimoire.Types.MethodNotImplementedHere(path)
        return {'value': self._call(path, *callarg, **callkw)}

    def _treeOp_impl_params(self, path, **kw):
        if (1, []) not in self._treeOp_impl_dir(path=path, treeOp='dir', depth=0)['value']:
            raise Grimoire.Types.MethodNotImplementedHere(path)
        return {'value': self._params(path)}

    def _treeOp_impl_dir(self, path, depth, **kw):
        if not depth and self.__dir_allowall__:
            return {'value': [(1, [])]}
        if self.__dir_exclude__:
            for exclude in self.__dir_exclude__:
                if (   Grimoire.Utils.isPrefix(exclude, path)
                       or (exclude[-1] == '' and exclude[:-1] == path)):
                    return {'value': []}
        return {'value': self._dir(path, depth)}

    # You may define these in user classes if you whish to.

    # __related_group__ = ['some', 'object', 'path']
    # __related_description__ = ['some', 'descriptive', 'path']
    # def _related(self, path, depth, objectPath, objectDepth):
    #     ...

    # You may override these in user classes if you whish to.
    __dir_allowall__ = True
    __dir_exclude__ = ()

    # Override these in a user-class
    def _call(self, path, *arg, **kw):
        raise NotImplementedError(self, '_call', path, *arg, **kw)

    def _dir(self, path, depth):
        raise NotImplementedError(self, '_dir', path, depth)

    def _params(self, path):
        raise NotImplementedError(self, '_params', path)

class Container(ImplementingHandling):
    __slots__ = []

    # Physical node API

    def _pathForChild(self, obj, extraPath = [], dynamic=False):
        if obj not in self._getChildren():
            raise AssertionError(self, obj, extraPath)
        return self._pathForSelf(extraPath, dynamic)

    def __unicode__(self, indentation = ''):
        return self.__description__(indentation) + ''.join([child.__unicode__(indentation + ' ') for child in self._getChildren()])

    # Logical node API

    def _treeOp_handle(self, treeOp, **kw):
        return getattr(self, "_treeOp_combine_" + treeOp,
                       self._treeOp_combine
                       )([child._treeOp_recurse for child in self._getChildren()],
                         treeOp=treeOp, **kw)

class SingleChildContainer(Container):
    __slots__ = ['_child']
    
    def __init__(self, child):
        child = Physical(child)
        ImplementingHandling.__init__(self)
        self._child = child
        child._setParent(self)

    def _getChildren(self):
        return [self._child]

    def _insert(self, *arg, **kw):
        return self._child._insert(*arg, **kw)

    def _remove(self, *arg, **kw):
        return self._child._remove(*arg, **kw)

class ThinSingleChildContainer(SingleChildContainer):
    def _treeOp_handle(self, **kw):
        return self._child._treeOp_recurse(**kw)

class Isolator(ThinSingleChildContainer):
    """An Isolator restricts the view of the world of a subtree's
    methods to that subtree.
    """
    __slots__ = []
    def __init__(self, child):
        ImplementingHandling.__init__(self)
        self._child = Physical(child)

    def _treeOp_recurse(self, path, wholePath, **kw):
        return self._child._treeOp_recurse(path=path, wholePath=path, **kw)

class AbstractRestrictor(ThinSingleChildContainer):
    __slots__ = ['_abilityObject']    
    
    def __init__(self, child, ability):
        ThinSingleChildContainer.__init__(self, child)
        self._abilityObject = ability

    # Physical node API

    def _ability(self):
        return self._abilityObject

    def __description__(self, indentation):
        return indentation + self.__class__.__name__ + ':' + unicode(self._ability()) + '\n'

class Hide(AbstractRestrictor):
    """Hide restricts the set of methods cisible on another Physical
    by means of an Ability-object, as defined in the Ability
    module. It does not in any way restrict calls to methods thusly
    made invisible.
    """
    __slots__ = []

    def __init__(self, child, ability = Grimoire.Types.Ability.List([(Grimoire.Types.Ability.Deny, [])])):
        AbstractRestrictor.__init__(self, child, ability)
        
    def _treeOp_combine_dir(self, fns, **kw):
        return []

    def _treeOp_handle_dir(self, path, **kw):
        def filterUnallowed((leaf, pth)):
            if not self._abilityObject(path + pth, not leaf):
                raise Grimoire.Utils.FilterOutError()
            return (leaf, pth)
        res = ThinSingleChildContainer._treeOp_handle(self, path=path, **kw)
        res['value'] = Grimoire.Utils.Map(filterUnallowed, res['value'])
        return res

class Restrictor(Hide):
    """A Restrictor restricts the set of methods available on another
    Physical by means of an Ability-object, as defined in the Ability
    module. Note that the Restrictor also hides all methods that are
    thusly removed.
    """
    __slots__ = []

    def __init__(self, child, ability = Grimoire.Types.Ability.List([(Grimoire.Types.Ability.Allow, [])])):
        AbstractRestrictor.__init__(self, child, ability)

    def _treeOp_handle_call(self, path, **kw):
        if not self._abilityObject(path) and not self._unlockedTree():
            raise Grimoire.Types.MethodNotImplementedHere(path)
        return ThinSingleChildContainer._treeOp_handle(self, path=path, **kw)

    def _treeOp_handle_implementor(self, path, **kw):
        if (1, []) in self._treeOp_recurse(path=path, treeOp='dir', depth=0, **kw)['value']:
            return self
        raise Grimoire.Types.MethodNotImplementedHere(path)

# Rename Cutter to TemporaryCutter or something, and introduce this one...
# class Cutter(SingleChildContainer):
#     """A Cutter cuts out a part of a Performer-object and presents it
#     as a (new) Physical-object, namely all methods with a common
#     prefix (basepath)."""
#     __slots__ = ['_basepath']
    
#     def __init__(self, child, basepath = [], temporary = True):
#         SingleChildContainer.__init__(self, child)
#         self._basepath = basepath

#     # Optimizations

#     def _chunk(self, extrapath):
#         return Cutter(self._child, self._path(extrapath))

#     # Physical node API

#     def _performer(self):
#         return self._physicalParent()

#     def _path(self, extraPath = []):
#         return self._basepath + extraPath

#     def _pathForChild(self, obj = None, extraPath = [], dynamic=False):
#         if not Grimoire.Utils.isPrefix(self._basepath, extraPath):
#             raise AssertionError(self, obj, extraPath)
#         return SingleChildContainer._pathForChild(self, obj, extraPath[len(self._basepath):], dynamic)

#     # Logical node API

#     def _treeOp_recurse(self, path, **kw):
#         return SingleChildContainer._treeOp_recurse(self, path=self._path(path), **kw)


def getTreevarFromRoot(root, path, varname):
    return root._treeOp(['directory', 'get', 'treevar'] + path, 'call', callarg=(['treevar', varname[1:]],), callkw={'cache':True})
getTreevarFromRoot = Grimoire.Utils.cachingFunction(getTreevarFromRoot)
    
def getTreevar(self, varname):
    path = self._pathForSelf()
    root = self._physicalGetpath(Grimoire.Types.TreeRoot)
    return getTreevarFromRoot(root, path, varname)
getTreevar = Grimoire.Utils.cachingFunction(getTreevar)

def getPrefix(tree, hasVar, prefix, prefixlen, path, expandVars = False):
    """Returns a tripple (ownprefix, ownprefixlen, which), where

    * ownprefix is prefix with variables expanded,

    * ownprefixlen is the length of ownprefix and

    * which is
      1 if ownprefix is a prefix of path,
      0 if they are equal and
      -1 if path is a prefix of ownprefix.

    If path is a prefix of ownprefix and expandVars is False, only
    variables in the matching part of prefix are expanded in
    ownprefix.
    """

    if not hasVar or not expandVars:
        which = Grimoire.Utils.whichPrefix(path, prefix)
        if which in (1, 0) or not hasVar:
            return (prefix, prefixlen, which)
        elif which == -1:
            def unlocked():
                # Path is a prefix of ownprefix:
                # check if there's treevars after the common prefix
                # that expands to nothing.
                pathlen = len(path)
                restPath = prefix[pathlen:]
                removed = 0
                for elem in restPath:
                    try:
                        if elem.startswith('$') and getTreevar(tree, elem) == []:
                            removed += 1;
                        else:
                            break;
                    except:
                        break
                return (prefix[:pathlen] + prefix[pathlen + removed:], prefixlen - removed, cmp(pathlen, prefixlen - removed))
            return tree._callWithUnlockedTree(unlocked)
    def unlocked():
        pathlen = len(path)
        dstprefix = []
        pos = 0
        pathpos = 0
        while pos < prefixlen:
            if pathpos < pathlen and path[pathpos] == prefix[pos]:
                dstprefix.append(prefix[pos])
                pos += 1
                pathpos += 1
                continue
            elif prefix[pos].startswith('$') and (pathpos < pathlen or expandVars):
                try:
                    varvalue = getTreevar(tree, prefix[pos])
                except Exception, e:
                    if pathpos < pathlen:
                        raise AttributeError(path)
                    dstprefix.append(prefix[pos])
                    pos += 1
                    continue
                if (    pathpos < pathlen
                    and Grimoire.Utils.whichPrefix(path[pathpos:], varvalue) is None):
                    return (dstprefix, len(dstprefix), None)
                dstprefix.extend(varvalue)
                pos += 1
                pathpos += len(varvalue)
                continue
            elif pathpos >= pathlen:
                dstprefix.append(prefix[pos])
                pos += 1
                continue
            return (dstprefix, len(dstprefix), None)
        dstprefixlen = len(dstprefix)
        return (dstprefix, dstprefixlen, cmp(pathlen, dstprefixlen))
    return tree._callWithUnlockedTree(unlocked)


class Prefixer(ThinSingleChildContainer):
    __slots__ = ['_prefix', '_prefixlen', '_hasVar']
    def __init__(self, prefix, child):
        ThinSingleChildContainer.__init__(self, child)
        self._prefix = prefix
        self._prefixlen = len(prefix)
        child._setBaseLevel(self._prefixlen)
        self._hasVar = False
        for name in prefix:
            if name.startswith('$'):
                self._hasVar = True
                break

    # Physical node API

    def _pathForChild(self, obj = None, extraPath = [], dynamic=False):
        return ThinSingleChildContainer._pathForChild(self, obj, self._prefix + extraPath, dynamic)

    def _insert(self, *arg, **kw):
        raise TypeError('Nodes can not be inserted in a Prefixer')
    
    def _remove(self, *arg, **kw):
        raise TypeError('Nodes can not be inserted in, nor removed from, a Prefixer')
    
    def __description__(self, indentation):
        return indentation + self.__class__.__name__ + ':' + '.'.join(self._prefix) + '\n'

    # Logical node API

    def _treeOp_handle(self, path, **kw):
        prefix, prefixlen, which = getPrefix(self, self._hasVar, self._prefix, self._prefixlen, path)
        if which in (None, -1): # same as not Grimoire.Utils.isPrefix(prefix, path)
            raise Grimoire.Types.MethodNotImplementedHere(path)
        return ThinSingleChildContainer._treeOp_handle(self, path=path[prefixlen:], **kw)

    def _treeOp_handle_count(self, **kw):
        return ThinSingleChildContainer._treeOp_handle(self, **kw)
        
    def _treeOp_handle_translate(self, path, **kw):
        prefix, prefixlen, which = getPrefix(self, self._hasVar, self._prefix, self._prefixlen, path)
        if which in (None, -1): # same as not Grimoire.Utils.isPrefix(prefix, path)
            raise Grimoire.Types.MethodNotImplementedHere(path)
        #print "Recurse from", self._pathForSelf(), "into", self._prefix
        res = ThinSingleChildContainer._treeOp_handle(self, path=path[prefixlen:], **kw)
        res['implementor'][0:0] = list(prefix)
        return res

    def _treeOp_handle_dir(self, path, treeOp, depth, **kw):
        ownprefix, ownprefixlen, which = getPrefix(self, self._hasVar, self._prefix, self._prefixlen, path, True)
        if which is None:
            return {'value': []}
        pathlen = len(path)
        # Path + depth is shorter than our prefix
        if which == -1 and pathlen + depth < ownprefixlen:
            if not ThinSingleChildContainer._treeOp_handle(self, path=[], treeOp=treeOp, depth=0, **kw):
                return {'value': []}
            return {'value': [(0, ownprefix[pathlen:pathlen + depth])]}
        res = ThinSingleChildContainer._treeOp_handle(self, path=path[ownprefixlen:], treeOp=treeOp,
                                                      depth=depth - max(0, (ownprefixlen - pathlen)), **kw)
        res['value'] = Grimoire.Utils.Map(
            lambda (leaf, path): (leaf, ownprefix[pathlen:] + path),
            res['value'])
        return res

    def _treeOp_handle_related(self, path, treeOp, depth, objectPath, objectDepth, **kw):
        ownprefix, ownprefixlen, which = getPrefix(self, self._hasVar, self._prefix, self._prefixlen, path, True)
        if which is None:
            return {'value': []}
        pathlen = len(path)
        # Path + depth is shorter than our prefix
        if which == -1 and pathlen + depth < ownprefixlen:
            return {'value': []}
        res =  ThinSingleChildContainer._treeOp_handle(self, path=path[ownprefixlen:],
                                                    treeOp=treeOp,
                                                    depth=depth - max(0, (ownprefixlen - pathlen)),
                                                    objectPath=objectPath, objectDepth=objectDepth, **kw)
        res['value'] = Grimoire.Utils.Map(
            lambda (leaf, objectPath, description, methodPath): (leaf, objectPath, description, ownprefix[pathlen:] + methodPath),
            res['value'])
        return res

class Composer(Container):
    """
    Composer combines several Performer-objects into one
    [Physical-object].
    """
    __slots__ = ['_children']
    
    def __init__(self, *children):
        ImplementingHandling.__init__(self)
        self._children = []
        for child in children:
            child = Physical(child)
            child._setParent(self)
            self._children.append(child)

    # Physical node API

    def _getChildren(self):
        return self._children

    def _insert(self, obj, first=False):
        if first:
            self._children.insert(0, obj)
        else:
            self._children.append(obj)
        obj._setParent(self)

    def _remove(self, obj, first=0):
        if not first:
            self._children.reverse()
        self._children.remove(obj)
        if not first:
            self._children.reverse()

    def _treeOp_recurse(self, **kw):
        return self._treeOp_handle(**kw)
    
class Base(Composer):
    """A Base object is a container for methods. Methods can not be
    incorporated as-is in a Grimoire tree, but must be grouped and
    wrapped up in Base objects.

    A Base object is created from a class inheriting the Base class,
    providing class variables of Method or OldSubMethod type.

    The methods so defined are available as methods on the Base
    object, with names as they are defined, but with any underscore
    exchanged for a dot.

    Example:

    Foo(Base):
        class fie_naja_hehe(Method):
            ...
        class muae_nana(Method):
            ...
    foo = Foo()
    foo.fie.naja.hehe(...)
    """
    _hide = []
    def __init__(self):
        ImplementingHandling.__init__(self)
        try:
            hide = getattr(self.__class__, '_hide')
        except AttributeError:
            hide = []
        methods = []
        for name, value in Grimoire.Utils.listClassAttr(self.__class__):
            if name.startswith('_'):
                continue
            method = getattr(self.__class__, name)
            if not Grimoire.Utils.isSubclass(method, Physical):
                continue
            if hasattr(method, '__path__'):
                path = method.__path__
            else:
                path = name.split('_')
            if hasattr(method, '__extrapath__'):
                path += method.__extrapath__
            method = method()
            method._setPhysicalBase(self)
            if path in hide:
                method = Hide(method)
            method = Prefixer(path, method)
            methods.append(method)
        Composer.__init__(self, *methods)

class Realoadable(SingleChildContainer):
    __slots__ = ['_genChild']
    def __init__(self, genChild):
        self._genChild = genChild
        self._treeOp_impl_reload(path=[], treeOp='reload')

    # Physical node API

    def _pathForChild(self, obj = None, extraPath = [], dynamic=False):
        return self._pathForSelf(SingleChildContainer._pathForChild(self, obj, extraPath, dynamic), dynamic)

    # Logical node API

    def _treeOp_impl_reload(self, *kw):
        SingleChildContainer.__init__(self.genChild())
        self._child._setParent(self)

