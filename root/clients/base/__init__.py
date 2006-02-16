import Grimoire, Grimoire.Performer, Grimoire.Types, Grimoire.Types.Ability, Grimoire.Utils, Grimoire.About, types, string, sys, traceback

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive


debugDirCache = 0
debugTree = 0
debugTranslations = 0
debugMethods = 1

class Performer(Grimoire.Performer.Base):
    class base(Grimoire.Performer.Method):
        def _call(performer):
            class Session(object):

                composer = Grimoire.Types.TextComposer

                class DirCacheNode:
                    def __init__(self, subNodes=None, leaf = 0, translation = None):
                        self.subNodes = subNodes or Grimoire.Utils.OrderedMapping()
                        self.oldSubNodes = Grimoire.Utils.OrderedMapping()
                        self.leaf = leaf
                        self.updated = 0
                        self.translation = translation
                    def invalidate(self):
                        self.oldSubNodes.update(self.subNodes)
                        self.subNodes = Grimoire.Utils.OrderedMapping()
                        self.leaf = 0
                        self.updated = 0
                    def validate(self):
                        self.oldSubNodes = Grimoire.Utils.OrderedMapping()
                        self.updated = 1

                class Result(object):
                    __slots__ = ['method', 'result', 'error']
                    def __init__(self, method = None, result = None, error = None):
                        self.method = method
                        self.result = result
                        self.error = error

                def __new__(cls, tree = None, extraTrees = [], *arg, **kw):
                    """The session might be initialized with a Gimoire tree, or
                    with a Grimoire expression. In the case of an expression, the
                    method Grimoire._.introspection.eval is used to evaluate
                    the expression. If such an expression is used and returns
                    something that is not a tree, that value will be returned by
                    the initializer of this class instead of an instance of the
                    class.
                    """
                    
                    self = object.__new__(cls)
                    self.dirCache = self.DirCacheNode()
                    self.__ = Grimoire.Performer.Hide(
                        Grimoire.Performer.Composer(
                            Grimoire.Performer.Prefixer(
                                ['introspection'],
                                Grimoire._.trees.introspection()),
                            Grimoire._.trees.local.load(__name__ + '._about'),
                            *extraTrees + [Grimoire.Performer.Isolator(Grimoire._)]),
                        Grimoire._.directory.get.parameters(
                            ['clients', 'base', 'hide'],
                            Grimoire.Types.Ability.List([(Grimoire.Types.Ability.Ignore, ['directory']),
                                                         (Grimoire.Types.Ability.Ignore, ['clients']),
                                                         (Grimoire.Types.Ability.Ignore, ['trees']),
                                                         (Grimoire.Types.Ability.Ignore, ['introspection']),
                                                         (Grimoire.Types.Ability.Allow, [])]),
                            False))
                    self._ = Grimoire.Performer.Logical(self.__)
                    self.defaultLanguage = 'en'

                    comment = None
                    tree = tree or self._.directory.get.parameters(['clients', 'base', 'tree'], '_', False)
                    if not Grimoire.Utils.isInstance(tree, Grimoire.Performer.Performer):
                        result = self._.introspection.eval(tree)
                        tree = Grimoire.Types.getValue(result)
                        comment = Grimoire.Types.getComment(result)
                        if not Grimoire.Utils.isInstance(tree, Grimoire.Performer.Performer):
                            return result
                    tree = Grimoire.Performer.Physical(tree)
                    if tree is not self.__: # Allow _ as tree expression without causing an endless loop.
                        self.insert([], tree, root = 1)

                    exprs = Grimoire._.directory.get.parameters(['clients', 'base', 'initcommands'], [], False)
                    for expr in exprs:
                        try:
                            self.eval(expr)
                        except Exception, e:
                            pass

                    self.__init__(*arg, **kw)

                    if comment is not None:
                        return Grimoire.Types.AnnotatedValue(self, comment)
                    return self

                def invalidateDirCache(self):
                    def invalidate(node):
                        node.invalidate()
                        for subNode in node.subNodes.itervalues():
                            invalidate(subNode)
                    invalidate(self.dirCache)

                def invalidateDirCachePath(self, path):
                    """Invalidates all nodes along a path down the tree (if
                    existing).
                    """
                    def invalidate(treeNode, restpath):
                        if restpath and restpath[0] in treeNode.subNodes:
                            invalidate(treeNode.subNodes[restpath[0]], restpath[1:])
                        treeNode.invalidate()
                    invalidate(self.dirCache, path)

                def getDirCacheNode(self, path, create=0):
                    treeNode = self.dirCache
                    restpath = path
                    while restpath:
                        if restpath[0] not in treeNode.subNodes:
                            if create:
                                if restpath[0] in treeNode.oldSubNodes:
                                    if debugDirCache: print "Rebirth of node before", restpath[0]
                                    node = treeNode.oldSubNodes[restpath[0]]
                                    node.invalidate()
                                else:
                                    if debugDirCache: print "New node before", restpath
                                    node = self.DirCacheNode()
                                treeNode.subNodes[restpath[0]] = node
                            else:
                                raise KeyError(path)
                        treeNode = treeNode.subNodes[restpath[0]]
                        restpath = restpath[1:]
                    return treeNode

                def updateDirCache(self, prefixPath, depth = Grimoire.Performer.UnlimitedDepth, reupdate=1):
                    """Updates depth levels down a branch of the tree. If reupdate
                    is not true, nodes with updated == 1 will not be updated
                    again.
                    """
                    subDepth = depth
                    if subDepth == -1:
                        subDepth = Grimoire.Performer.UnlimitedDepth
                    if subDepth > 0:
                        node = self.getDirCacheNode(prefixPath, 1)
                        if reupdate or not node.updated:
                            if debugDirCache: print "Reupdate", prefixPath, subDepth
                            node = self.getDirCacheNode(prefixPath, 1)
                            translatedPaths = []
                            for (leaf, path) in Grimoire.Utils.SortedList(self.__._getpath(path=['introspection', 'dir'] + prefixPath
                                                                                           )(subDepth),
                                                                          lambda x, y: cmp(len(y[1]), len(x[1]))):
                                path = prefixPath + path
                                subNode = self.getDirCacheNode(path, 1)
                                if leaf:
                                    subNode.leaf = 1
                                if len(path) < subDepth - 1:
                                    subNode.validate()
                                if path not in translatedPaths and subNode.translation is None:
                                    translatedPaths += [path]
                                    if path: # The root-path can not be translated
                                        try:
                                            subNode.translation = self.getTranslationTable(path[:-1])(path[-1])
                                        except Grimoire.Utils.UntranslatableError:
                                            pass
                            node.validate()
                        else:
                            for key in node.subNodes.iterkeys():
                                self.updateDirCache(prefixPath + [key], subDepth - 1, reupdate)
                        return node
                    return None

                def updatedDirCachePath(self, path, depth = 1, reupdate=0):
                    """Updates all nodes along a path down the tree,
                    and then depth nodes from there (that is, if depth
                    == 1, only nodes along the path will get
                    updated). If reupdate is not true, nodes with
                    updated == 1 will not be updated again.
                    """
                    for index in xrange(0, len(path)):
                        self.updateDirCache(path[:index], 1, reupdate)
                    return self.updateDirCache(path, depth, reupdate)

                def insert(self, path, obj, root = False, isolate = True, **kw):
                    try:
                        self.defaultLanguage = Grimoire.Types.getValue(Grimoire.Performer.Logical(obj).directory.get.user(['language']))
                    except (AttributeError, TypeError):
                        pass
                    if isolate:
                        obj = Grimoire.Performer.Isolator(obj)
                    if not root:
                        obj = Grimoire.Performer.Composer(obj, Grimoire._.trees.local.load(__name__ + '._logout'))
                    obj = Grimoire.Performer.Prefixer(path, obj)
                    if not root:
                        directory = Grimoire._.directory.new()
                        obj = Grimoire.Performer.Composer(
                            obj,
                            Grimoire.Performer.Restrictor(
                                directory, Grimoire.Types.Ability.List([])))
                        def unlocked():
                            directory.directory.set.treeinfo(['local', 'client', 'logout', 'session'], self)
                            directory.directory.set.treeinfo(['local', 'client', 'logout', 'tree'], obj)
                            directory.directory.set.treeinfo(['local', 'client', 'logout', 'path'], path)
                        obj._callWithUnlockedTree(unlocked)
                    self.__._insert(obj, **kw)
                    self.getDirCacheNode(path, 1).invalidate()
                    return obj

                def insertUnique(self, path, obj, **kw):
                    def uniquePath(node, path):
                        for item in path:
                            node = node.subNodes[item]
                        return path + [unicode(len(node.subNodes))]
                    self.updatedDirCachePath(path)
                    upath = uniquePath(self.dirCache, path)
                    self.insert(upath, obj, **kw)
                    return upath

                def remove(self, path, obj):
                    self.__._remove(obj)
                    self.invalidateDirCache(path, True)

                def defaultMethod(self):
                    path = []
                    self.updatedDirCachePath(path)
                    node = self.dirCache
                    if len(node.subNodes) == 2:
                        for key in node.subNodes:
                            if key != 'about':
                                path += [key]
                                self.updatedDirCachePath(path)
                                node = node.subNodes[key]
                    while len(node.subNodes) == 1:
                        key = node.subNodes.keys()[0]
                        path += [key]
                        self.updatedDirCachePath(path)
                        node = node.subNodes[key]
                    if len(node.subNodes) != 0 or not node.leaf:
                        return None
                    return path

                def getMethodPath(self, path = None):
                    return path or ()

                def getTranslationTable(self, path = None, language = None):
                    language = language or self.defaultLanguage
                    path = self.getMethodPath(path)
                    translationObj = self.__._getpath(path=['introspection', 'translate'] + list(path))
                    def translationTable(message):
                        if debugTranslations: print "Translate:", path, language, message
                        return translationObj(language, message)
                    return Grimoire.Utils.cachingFunction(translationTable)
                getTranslationTable = Grimoire.Utils.cachingFunction(getTranslationTable)

                def getComposer(self, path = None, *arg, **kw):
                    trtbl = self.getTranslationTable(path, *arg, **kw)
                    class Composer(self.composer):
                        def translationTable(self, *arg, **kw):
                            return trtbl(*arg, **kw)
                        translationTable = classmethod(translationTable)
                        currentMethod = list(self.getMethodPath(path))
                    return Composer

                def handleResult(self, method, result):
                    res = Grimoire.Types.getValue(result)
                    if Grimoire.Utils.isInstance(res, Grimoire.Performer.Performer):
                        path = self.insertUnique(list(method), res)
                        return Grimoire.Types.AnnotatedValue(
                            None,
                            Grimoire.Types.getComment(
                                result,
                                "login returned a set of methods"))
                    return result

                def handleExecution(self, method, execJob):
                    result = self.Result()
                    try:
                        result.result = execJob()
                    except:
                        result.error = sys.exc_info()[1]
                        if debugMethods:
                            traceback.print_exc()
                    if result.error is None:
                        result.result = self.handleResult(method, result.result)
                    return result

                def handleCall(self, method, args):
                    fn = self.__._getpath(path=list(method))
                    return self.handleExecution(method,
                                                lambda: fn(*(args.args + args.extraArgs),
                                                           **args.kws))
                
                def eval(self, expression):
                    # FIXME: Call this handleEval...
                    return self.handleExecution(
                        self._.introspection.methodOfExpression(expression),
                        lambda: self._.introspection.eval(expression))
                
            return Session
        _call = Grimoire.Utils.cachingFunction(_call)
        def _params(self):
            return A(Ps(),
                     'The Session class nearly implements a Grimoire client application. Except the last bit - the UI. It provides such services as caching of the directory tree listing, translation of tree entries, expansion/callaping of subtrees for clients that themselves implement the tree rendering and handling of default trees. To implement a real client, you might need both to subclass and to wrap this class. In subclassing it, you may subclass the class used to create directory cache tree nodes by assigning the class variable DirCacheNode with the new subclass to use')

    class form(Grimoire.Performer.Method):
        def _call(performer):
            Session = performer._getpath(Grimoire.Types.MethodBase).base()
            class FormSession(Session):
                class Selection(object):
                    __slots__ = ['method', 'params', 'result']
                    def __init__(self):
                        self.method = None
                        self.params = None
                        self.result = None
 
                def __init__(self, *arg, **kw):
                    self.selection = self.Selection()
                    super(FormSession, self).__init__(*arg, **kw)

                def getMethodPath(self, path = None):
                    if path is None and self.selection:
                        path = self.selection.method
                    return path or ()

                def select(self, method):
                    self.selection.__init__()
                    self.selection.method = method
                    self.selection.params = self.__._getpath(
                        path=['introspection', 'params'] + list(method))()                    
                    if (    not self.selection.params.arglist
                        and not self.selection.params.resargstype
                        and not self.selection.params.reskwtype):
                        self.handleCall(self.selection.method,
                                        Grimoire.Types.getValue(self.selection.params)())

                def handleExecution(self, *arg, **kw):
                    self.selection.result = super(FormSession, self).handleExecution(*arg, **kw)
                    return self.selection.result

                def handleCall(self, method = None, args = []):
                    if method is None:
                        method = self.selection.method
                    return super(FormSession, self).handleCall(method, args)
                    
                def drawSelection(self, selection):
                    pass
                                  
                def renderSelection(self):
                    result = Grimoire.Types.Paragraphs()
                    if self.selection.result and not self.selection.result.error:
                        result.append(self.selection.result.result)
                    else:
                        if self.selection.result and self.selection.result.error:
                            result.append(self.selection.result.error)
                        if self.selection.params:
                            result.append(self.selection.params)
                    self.drawSelection(
                        self.composer(result))
                
                def gotoLocation(self, location):
                    try:
                        method = self._.introspection.methodOfExpression(location, True)
                    except Exception: # We've got a complex expression...
                        method = None

                    if method:
                        self.select(method)
                    else:
                        self.eval(location)
                    return self.renderSelection()
                
                def applyForm(self, args):
                    self.handleCall(self.selection.method, args)
                    self.renderSelection()

            return FormSession
        _call = Grimoire.Utils.cachingFunction(_call)
        def _params(self):
            return A(Ps(),
                     'Session sub-class that adds form-based client helper methods.')

    class renderable(Grimoire.Performer.Method):
        def _call(performer):
            Session = performer._getpath(Grimoire.Types.MethodBase).base()
            class RenderableSession(Session):
                class DirCacheNode(Session.DirCacheNode):
                    def __init__(self, expanded = 0, *arg, **kw):
                        Session.DirCacheNode.__init__(self, *arg, **kw)
                        self.expanded = expanded

                def expand(self, path, depth = Grimoire.Performer.UnlimitedDepth):
                    if debugTree: print "Expand:", path, depth
                    node = self.updatedDirCachePath(path, depth)
                    def expand(node, depth):
                        node.expanded = 1
                        if depth > 1:
                            for name in node.subNodes.iterkeys():
                                expand(node.subNodes[name], depth - 1)
                    expand(self.updatedDirCachePath(path, depth), depth)

                def expandPath(self, path, depth = Grimoire.Performer.UnlimitedDepth):
                    if debugTree: print "ExpandPath:", path, depth
                    for index in xrange(0, len(path)):
                        self.expand(path[:index], 1)
                    return self.expand(path, depth)

                def collapse(self, path):
                    if debugTree: print "Collapse:", path
                    self.updatedDirCachePath(path).expanded = 0

                def insertUnique(self, path, obj, **kw):
                    upath = super(RenderableSession, self).insertUnique(path, obj, **kw)
                    self.expand(list(path), 1)
                    self.expand(upath, 1)
                    return upath

                def renderTree(self, renderEntry, *args, **kw):
                    def renderTreeEntries(node, path, subNodes, subNode, res, *args, **kw):
                        if node.expanded and not node.updated:
                            self.updateDirCache(path, 1, 0)
                        (nres, nargs, nkw) = renderEntry(node, path, subNodes, subNode, res, *args, **kw)
                        if node.expanded:
                            subNodes = len(node.subNodes)
                            subNodeNr = 0
                            for name, subNode in node.subNodes.iteritems():
                                nres = renderTreeEntries(subNode, path + [name], subNodes, subNodeNr, nres, *nargs, **nkw)
                                subNodeNr += 1
                        return nres
                    return renderTreeEntries(self.dirCache, [], 1, 0, None, *args, **kw)

                def renderTreeToText(self):
                    pictIcon = (('[=]', '[=]'),
                                ('\\_\\', '\\_/'))            
                    pictExpander = ((('|--', '`--'),
                                     ('|--', '`--')),
                                    (('|-+', '`-+'),
                                     ('|-.', '`-.')))
                    def renderEntry(node, path, sibblings, sibbling, res, indent='', ):
                        subNodes = len(node.subNodes)
                        res = res or ''
                        res += indent
                        res += pictExpander[subNodes > 0 or not node.updated][node.expanded][sibbling == sibblings - 1]
                        res += pictIcon[subNodes > 0][node.expanded]
                        if node.translation is not None:
                            res += node.translation
                        elif path:
                            res += path[-1]
                        else:
                            res += 'Grimoire'
                        res += "\n"
                        return (res,
                                (indent + ['|  ', '   '][sibbling == sibblings - 1],),
                                {})

                    return self.renderTree(renderEntry)
            
            return RenderableSession
        _call = Grimoire.Utils.cachingFunction(_call)
        def _params(self):
            return A(Ps(),
                     'Session sub-class that adds the notion of expanded and unexpanded branches, suitable for rendering a user-expandable/collapsable tree')

