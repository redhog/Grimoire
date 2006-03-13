import Grimoire, Grimoire.Performer, Grimoire.Types, Grimoire.Types.Ability, Grimoire.Utils
import Grimoire.Utils.Serialize.Writer, Grimoire.Utils.Serialize.Types, Grimoire.Utils.Password
import types, string, sys, traceback, StringIO

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive


debugDirCache = 0
debugTree = 0
debugTranslations = 0
debugMethods = 1
debugUpdates = 0
debugCalls = 0

class Performer(Grimoire.Performer.Base):
    class base(Grimoire.Performer.Method):
        def _call(performer):
            class Session(object):

                composer = Grimoire.Types.TextComposer
                sessionPath = ['parameters', 'clients']
                hide = Grimoire.Types.Ability.List([(Grimoire.Types.Ability.Ignore, ['directory']),
                                                    (Grimoire.Types.Ability.Ignore, ['clients']),
                                                    (Grimoire.Types.Ability.Ignore, ['trees']),
                                                    (Grimoire.Types.Ability.Ignore, ['introspection']),
                                                    (Grimoire.Types.Ability.Allow, [])])

                class Result(object):
                    __slots__ = ['method', 'result', 'error']
                    def __init__(self, method = None, result = None, error = None):
                        self.method = method
                        self.result = result
                        self.error = error

                class View(object):
                    viewPath = []
                    parent = None

                    class Send(object):
                        class __SendMethod(object):
                            def __init__(self, view, method):
                                self.view = view
                                self.method = method
                            def __call__(self, *arg, **kw):
                                return self.view.viewOp(self.method, *arg, **kw)
                        def __init__(self, view):
                            self.__view = view
                        def __getattr__(self, name):
                            return self.__SendMethod(self.__view, name)
                            
                    def __init__(self, session, path, parent = None, **kw):
                        self.session = session
                        self.path = path
                        self.parent = parent
                        if self.parent:
                            self.root = self.parent.root
                        else:
                            self.root = self
                        self.send = self.Send(self)
                        
                    def viewOp(self, operation, *arg, **kw):
                        try:
                            return self.root.viewOpRecurse(operation, *arg, **kw)
                        except Grimoire.Types.MethodNotImplementedHere:
                            return []

                    def viewOpRecurse(self, operation, *arg, **kw):
                        if not hasattr(self, operation):
                            raise Grimoire.Types.MethodNotImplementedHere
                        return [getattr(self, operation)(*arg, **kw)]

                class ViewGroup(View):
                    def __init__(self, *arg, **kw):
                        super(Session.ViewGroup, self).__init__(*arg, **kw)
                        self.children = {}
                        
                    def addView(self, path = (), viewClass = None, **kw):
                        path = tuple(path)
                        if viewClass is None:
                            viewClass = self.TreeView
                        view = viewClass(path = self.path + path, session = self.session, parent = self, **kw)
                        self.children[path] = view
                        return view

                    def deleteView(self, path):
                        del self.children[path]

                    def viewOpRecurse(self, operation, *arg, **kw):
                        result = []
                        for child in self.children.itervalues():
                            try:
                                result.append(child.viewOpRecurse(operation, *arg, **kw))
                            except Grimoire.Types.MethodNotImplementedHere:
                                pass
                        return result
                        
                class TreeView(View):
                    hide = Grimoire.Types.Ability.List([(Grimoire.Types.Ability.Ignore, ['directory']),
                                                        (Grimoire.Types.Ability.Ignore, ['clients']),
                                                        (Grimoire.Types.Ability.Ignore, ['trees']),
                                                        (Grimoire.Types.Ability.Ignore, ['introspection']),
                                                        (Grimoire.Types.Ability.Allow, [])]) 
                    prefix = []
                   
                    class DirCacheNode(object):
                        __slots__ = ['view', 'parent', 'path', 'subNodes', 'oldSubNodes',
                                     'leaf', 'updated', 'translation']
                        def __init__(self, view, parent = None, name = None, subNodes = None,
                                     leaf = None, translation = None):
                            """Note: The theory is that either both of
                            parent and name are None, or neither of
                            them"""
                            self.view = view
                            self.subNodes = subNodes or Grimoire.Utils.OrderedMapping()
                            self.oldSubNodes = Grimoire.Utils.OrderedMapping()
                            self.leaf = leaf or 0
                            self.updated = subNodes is not None and leaf is notNone
                            self.translation = translation
                            self.setParent(parent, name)
                        def setParent(self, parent, name):
                            self.parent = parent
                            self.path = []
                            if parent:
                                parent.subNodes[name] = self
                                self.path = parent.path + [name]
                        def reparent(self, parent, name):
                            self.setParent(parent, name)
                            self.invalidate()
                        def invalidate(self):
                            if self.updated:
                                self.oldSubNodes.update(self.subNodes)
                                self.subNodes = Grimoire.Utils.OrderedMapping()
                                self.leaf = 0
                                self.updated = 0
                        def validate(self):
                            if not self.updated:
                                self.oldSubNodes = Grimoire.Utils.OrderedMapping()
                                self.updated = 1

                    def __init__(self, hide = None, **kw):
                        super(Session.TreeView, self).__init__(**kw)
                        self.dirCache = self.DirCacheNode(view = self)
                        self.__ = self.session.__
                        self.hide = hide or Grimoire.__._getpath(
                            Grimoire.Types.TreeRoot,
                            path = ['directory', 'get'] + self.session.sessionPath + self.viewPath + list(self.path)
                            )(['view', 'hide'], self.hide, False)
                        self.prefix = hide or Grimoire.__._getpath(
                            Grimoire.Types.TreeRoot,
                            path = ['directory', 'get'] + self.session.sessionPath + self.viewPath + list(self.path)
                            )(['view', 'prefix'], self.prefix, False)
                        self.__ = Grimoire.Performer.Composer(
                            Grimoire.Performer.Hide(Grimoire.Performer.Prefixer(['introspection'],
                                                                                Grimoire._.trees.introspection()),
                                                    Grimoire.Types.Ability.List([(Grimoire.Types.Ability.Deny, ['introspection'])])),
                            Grimoire.Performer.Hide(Grimoire.Performer.Isolator(self.__),
                                                    self.hide)._physicalGetpath(path=self.prefix))
                        self._ = Grimoire.Performer.Logical(self.__)

                    def getComposer(self, *arg, **kw):
                        class Composer(self.session.getComposer(*arg, **kw)):
                            view = self
                        return Composer

                    def getDirCacheNode(self, path, create = False, treeNode = None):
                        treeNode = treeNode or self.dirCache
                        restpath = path
                        while restpath:
                            if restpath[0] in treeNode.subNodes:
                                node = treeNode.subNodes[restpath[0]]
                            else:
                                if create:
                                    if restpath[0] in treeNode.oldSubNodes:
                                        if debugDirCache: print "Rebirth of node before", restpath[0]
                                        node = treeNode.oldSubNodes[restpath[0]]
                                        node.reparent(treeNode, restpath[0])
                                    else:
                                        if debugDirCache: print "New node before", restpath
                                        node = self.DirCacheNode(view = self,
                                                                 parent = treeNode,
                                                                 name = restpath[0])
                                else:
                                    raise KeyError(path)
                            treeNode = node
                            restpath = restpath[1:]
                        return treeNode

                    def invalidateDirCache(self, path = [], treeNode = None, create = False):
                        node = self.getDirCacheNode(path, create, treeNode = treeNode)
                        node.invalidate()
                        return node
                    
                    def updateDirCache(self, prefixPath, depth = Grimoire.Performer.UnlimitedDepth, reupdate=0, treeNode = None):
                        """Updates depth levels down a branch of the tree. If reupdate
                        is not true, nodes with updated == 1 will not be updated
                        again.
                        """
                        if debugUpdates: print "Update:", prefixPath, depth
                        subDepth = depth
                        if subDepth == -1:
                            subDepth = Grimoire.Performer.UnlimitedDepth
                        if subDepth > 0:
                            node = self.getDirCacheNode(prefixPath, 1, treeNode = treeNode)
                            if node.parent: assert(node.parent.updated)
                            if reupdate:
                                node.invalidate()
                            if not node.updated:
                                if debugDirCache: print "Reupdate", treeNode, prefixPath, subDepth
                                translatedPaths = []
                                for (leaf, path) in Grimoire.Utils.SortedList(
                                        self.__._getpath(path=['introspection', 'dir'] + node.path
                                                         )(subDepth),
                                        lambda x, y: cmp(len(y[1]), len(x[1]))):
                                    subNode = self.getDirCacheNode(path, 1, treeNode = node)
                                    path = node.path + path
                                    if leaf:
                                        subNode.leaf = 1
                                    if len(path) < subDepth - 1:
                                        subNode.validate()
                                    if path not in translatedPaths and subNode.translation is None:
                                        translatedPaths += [path]
                                        if path: # The root-path can not be translated
                                            try:
                                                subNode.translation = self.session.getTranslationTable(
                                                    path[:-1]
                                                    )(path[-1])
                                            except Grimoire.Utils.UntranslatableError:
                                                pass
                                node.validate()
                            elif subDepth > 1:
                                for subNode in node.subNodes.itervalues():
                                    self.updateDirCache([], subDepth - 1, reupdate, treeNode = subNode)
                            return node
                        return None

                    def updateDirCachePath(self, path, depth = 1, reupdate=0, treeNode = None):
                        """Updates all nodes along a path down the tree,
                        and then depth nodes from there (that is, if depth
                        == 1, only nodes along the path will get
                        updated). If reupdate is not true, nodes with
                        updated == 1 will not be updated again.
                        """
                        if not path:
                            return self.updateDirCache([], depth, reupdate, treeNode)
                        node = self.updateDirCache([], 1, reupdate, treeNode)
                        for item, name in enumerate(path):
                            if item == len(path) - 1:
                                return self.updateDirCache([name], depth, reupdate, node)
                            node = self.updateDirCache([name], 1, reupdate, node)
                            
                    def insert(self, path, treeNode = None, root = False, **kw):
                        return self.invalidateDirCache(path, create = True, treeNode = treeNode)

                    def remove(self, path, treeNode = None, **kw):
                        if path:
                            path = path[:-1]
                        else:
                            treeNode = treeNode.parent
                        return self.invalidateDirCache(path, treeNode = treeNode)

                    def traverseTree(self, traverseEntry, traverseSubEntries, res, *args, **kw):
                        def traverseTreeEntries(node, subNodeNr, res, *args, **kw):
                            (nres, nargs, nkw) = traverseEntry(node, subNodeNr, res, *args, **kw)
                            if traverseSubEntries(node, res, *args, **kw):
                                if node.updated:
                                    subNodes = node.subNodes
                                else:
                                    subNodes = node.oldSubNodes
                                for subNodeNr, (name, subNode) in enumerate(subNodes.iteritems()):
                                    nres = traverseTreeEntries(subNode, subNodeNr, nres, *nargs, **nkw)
                            return nres
                        return traverseTreeEntries(self.dirCache, 0, res, *args, **kw)

                    def debugRenderTreeToText(self):
                        pictExpander = ((('|?-', '`?-'),
                                         ('|?o', '`?o')),
                                        (('|--', '`--'),
                                         ('|-o', '`-o')))
                        def renderEntry(node, sibling, res, indent=''):
                            path = node.path
                            siblings = node.parent and len(node.parent.subNodes) or 1
                            subNodes = (node.updated and len(node.subNodes)) or len(node.oldSubNodes)
                            res += indent
                            res += pictExpander[node.updated][node.leaf][sibling == siblings - 1]
                            if node.translation is not None:
                                res += node.translation
                            elif node.path:
                                res += node.path[-1]
                            else:
                                res += 'Grimoire'
                            res += "\n"
                            return (res,
                                    (indent + ['|  ', '   '][sibling == siblings - 1],),
                                    {})
                        def renderSubEntries(*arg, **kw):
                            return True
                        return self.traverseTree(renderEntry, renderSubEntries, '')

                def __new__(cls, tree = None, extraTrees = [], initCommands = None, **kw):
                    """The session might be initialized with a Gimoire tree, or
                    with a Grimoire expression. In the case of an expression, the
                    method Grimoire._.introspection.eval is used to evaluate
                    the expression. If such an expression is used and returns
                    something that is not a tree, that value will be returned by
                    the initializer of this class instead of an instance of the
                    class.
                    """
                    
                    self = object.__new__(cls)

                    class Composer(self.composer):
                        session = self
                    self.composer = Composer
                    self.views = {}
                    
                    self.__ = Grimoire.Performer.Composer(
                        Grimoire.Performer.Prefixer(
                            ['introspection'],
                            Grimoire._.trees.introspection()),
                        Grimoire._.trees.local.load(__name__ + '._about'),
                        *extraTrees + [Grimoire.Performer.Isolator(Grimoire._)])
                    self._ = Grimoire.Performer.Logical(self.__)
                    self.defaultLanguage = 'en'

                    self.hide = Grimoire.__._getpath(
                            Grimoire.Types.TreeRoot,
                            path = ['directory', 'get'] + self.sessionPath
                            )(['child', 'hide'], self.hide, False)

                    comment = None
                    tree = tree or self.__._getpath(
                        Grimoire.Types.TreeRoot,
                        path = ['directory', 'get'] + self.sessionPath
                        )(['tree'], '_', False)
                    if not Grimoire.Utils.isInstance(tree, Grimoire.Performer.Performer):
                        result = self._.introspection.eval(tree)
                        tree = Grimoire.Types.getValue(result)
                        comment = Grimoire.Types.getComment(result)
                        if not Grimoire.Utils.isInstance(tree, Grimoire.Performer.Performer):
                            return result
                    tree = Grimoire.Performer.Physical(tree)
                    if tree is not self.__: # Allow _ as tree expression without causing an endless loop.
                        self.insert([], tree, root = 1)

                    initCommands = self.__._getpath(
                        Grimoire.Types.TreeRoot,
                        path = ['directory', 'get'] + self.sessionPath
                        )(['initcommands'], all=True) + [initCommands]

                    initCommandsResults = []
                    for initCommand in Grimoire.Utils.Flatten(initCommands):
                        try:
                            initCommandsResults.append(self.eval(initCommand))
                        except Exception, e:
                            initCommandsResults.append(e)

                    if initCommandsResults:
                        initCommandsResults = Grimoire.Types.Paragraphs(*initCommandsResults)
                        if comment is not None:
                            initCommandsResults.insert(0, comment)
                        comment = initCommandsResults
                        
                    self.__init__(**kw)

                    if comment is not None:
                        return Grimoire.Types.AnnotatedValue(self, comment)
                    return self

                # View operations

                def addView(self, path = (), viewClass = None, **kw):
                    path = tuple(path)
                    if viewClass is None:
                        viewClass = self.TreeView
                    view = viewClass(path = path, session = self, **kw)
                    self.views[path] = view
                    return view

                def deleteView(self, path):
                    del self.views[path]
                    
                def invalidateDirCache(self, *arg, **kw):
                    for view in self.views.itervalues():
                        view.send.invalidateDirCache(*arg, **kw)

                def updateDirCache(self, *arg, **kw):
                    """Updates depth levels down a branch of the tree. If reupdate
                    is not true, nodes with updated == 1 will not be updated
                    again.
                    """
                    return dict([(path, view.send.updateDirCache(*arg, **kw))
                                 for path, view in self.views.iteritems()])

                def updateDirCachePath(self, *arg, **kw):
                    """Updates all nodes along a path down the tree,
                    and then depth nodes from there (that is, if depth
                    == 1, only nodes along the path will get
                    updated). If reupdate is not true, nodes with
                    updated == 1 will not be updated again.
                    """
                    return dict([(path, view.send.updateDirCachePath(*arg, **kw))
                                 for path, view in self.views.iteritems()])
                                
                # Tree operations

                def insert(self, path, obj, root = False, isolate = True, **kw):
                    try:
                        self.defaultLanguage = Grimoire.Types.getValue(
                            Grimoire.Performer.Logical(obj).directory.get.user(['language']))
                    except (AttributeError, TypeError):
                        pass
                    if isolate:
                        obj = Grimoire.Performer.Isolator(obj)
                    if not root:
                        directory = Grimoire._.directory.new()
                        obj = Grimoire.Performer.Composer(
                            obj,
                            Grimoire.Performer.Isolator(
                                Grimoire.Performer.Composer(
                                    Grimoire.Performer.Restrictor(
                                        directory, Grimoire.Types.Ability.List([])),
                                    Grimoire._.trees.local.load(__name__ + '._logout'))))
                    if self.hide:
                        obj = Grimoire.Performer.Hide(obj, self.hide)

                    obj = Grimoire.Performer.Prefixer(path, obj)
                    if not root:
                        def unlocked():
                            directory.directory.set.treeinfo(['local', 'client', 'logout', 'session'], self)
                            directory.directory.set.treeinfo(['local', 'client', 'logout', 'tree'], obj)
                            directory.directory.set.treeinfo(['local', 'client', 'logout', 'path'], path)
                        Grimoire.Performer.Physical(directory)._callWithUnlockedTree(unlocked)
                    self.__._insert(obj, **kw)
                    for viewpath, view in self.views.iteritems():
                        view.send.insert(path, root = root, **kw)
                    return obj

                def insertUnique(self, path, obj, **kw):
                    uniqueName = unicode(len(set([
                        tuple(subPath)
                        for (leaf, subPath)
                        in Grimoire.Utils.SortedList(
                            self.__._getpath(path=['introspection', 'dir'] + path)(1))
                        ])))
                    path = path + [uniqueName]
                    self.insert(path, obj, **kw)
                    return path

                def remove(self, path, obj, **kw):
                    self.__._remove(obj)
                    for view in self.views.itervalues():
                        view.send.remove(path, **kw)

                # Method operations

                def defaultMethod(self):
                    path = []
                    self.updateDirCachePath(path)
                    node = self.dirCache
                    if len(node.subNodes) == 2:
                        for key in node.subNodes:
                            if key != 'about':
                                path += [key]
                                self.updateDirCachePath(path)
                                node = node.subNodes[key]
                    while len(node.subNodes) == 1:
                        key = node.subNodes.keys()[0]
                        path += [key]
                        self.updateDirCachePath(path)
                        node = node.subNodes[key]
                    if len(node.subNodes) != 0 or not node.leaf:
                        return None
                    return path

                def getTranslationTable(self, path = (), language = None):
                    language = language or self.defaultLanguage
                    translationObj = self.__._getpath(path=['introspection', 'translate'] + list(path))
                    def translationTable(message):
                        if debugTranslations: print "Translate:", path, language, message
                        return translationObj(language, message)
                    return Grimoire.Utils.cachingFunction(translationTable)
                getTranslationTable = Grimoire.Utils.cachingFunction(getTranslationTable)

                def getComposer(self, path = (), *arg, **kw):
                    trtbl = self.getTranslationTable(path, *arg, **kw)
                    class Composer(self.composer):
                        def translationTable(self, *arg, **kw):
                            return trtbl(*arg, **kw)
                        translationTable = classmethod(translationTable)
                        currentMethod = list(path)
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

                def handleCall(self, method, args, handleExecution = None):
                    if debugCalls: print "Call to method:", method
                    fn = self.__._getpath(path=list(method))
                    return (handleExecution or self.handleExecution)(method,
                                                lambda: fn(*(args.args + args.extraArgs),
                                                           **args.kws))
                
                def eval(self, expression, handleExecution = None):
                    # FIXME: Call this handleEval...
                    return (handleExecution or self.handleExecution)(
                        self._.introspection.methodOfExpression(expression),
                        lambda: self._.introspection.eval(expression))
                
            return Session
        _call = Grimoire.Utils.cachingFunction(_call)
        def _params(self):
            return A(Ps(),
                     'The Session class nearly implements a Grimoire client application. Except the last bit - the UI. It provides such services as caching of the directory tree listing, translation of tree entries, expansion/callaping of subtrees for clients that themselves implement the tree rendering and handling of default trees. To implement a real client, you might need both to subclass and to wrap this class. In subclassing it, you may subclass the class used to create directory cache tree nodes by assigning the class variable DirCacheNode with the new subclass to use')

    class numpath(Grimoire.Performer.Method):
        def _call(performer):
            Session = performer._getpath(Grimoire.Types.MethodBase).base()
            class NumpathSession(Session):
                class TreeView(Session.TreeView):
                    class DirCacheNode(Session.TreeView.DirCacheNode):
                        __slots__ = ['numpath']
                        def setParent(self, parent, name):
                            super(NumpathSession.TreeView.DirCacheNode, self).setParent(parent, name)
                            if parent:
                                self.numpath = parent.numpath + (parent.subNodes.__keys__.index(name),)
                            else:
                                self.numpath = ()
                        def __unicode__(self):
                            if self.translation is not None:
                                text = self.translation
                            elif self.path:
                                text = self.path[-1]
                            else:
                                text = 'Grimoire' 
                            if not self.leaf:
                                text = "<span foreground='#999999'>" + text + "</span>"
                            return text

                    def updateDirCacheNumPath(self, numpath, depth = 1, reupdate=0, treeNode = None):
                        """Updates all nodes along a numeric path down the tree,
                        and then depth nodes from there (that is, if depth
                        == 1, only nodes along the path will get
                        updated). If reupdate is not true, nodes with
                        updated == 1 will not be updated again.
                        """
                        try:
                            node = treeNode
                            if not numpath:
                                return self.updateDirCache([], depth, reupdate, treeNode)
                            node = self.updateDirCache([], 1, reupdate, treeNode)
                            for item, index in enumerate(numpath):
                                name = node.subNodes.__keys__[index]
                                if item == len(numpath) - 1:
                                    return self.updateDirCache([name], depth, reupdate, node)
                                node = self.updateDirCache([name], 1, reupdate, node)
                        except Exception, e:
                            print self.debugRenderTreeToText()
                            if node:
                                print node.path, index, node.subNodes.__keys__
                            print numpath, depth, reupdate, treeNode
                            traceback.print_exc()
                            raise e

            return NumpathSession
        _call = Grimoire.Utils.cachingFunction(_call)
        def _params(self):
            return A(Ps(),
                     'Session sub-class that adds support for numeric (index-based) paths.')

    class form(Grimoire.Performer.Method):
        def _call(performer):
            Session = performer._getpath(Grimoire.Types.MethodBase).base()
            class FormSession(Session):
                class TreeView(Session.TreeView):
                    class DirCacheNode(Session.TreeView.DirCacheNode): pass
                    def __init__(self, **kw):
                        super(FormSession.TreeView, self).__init__(**kw)
                        self.selections = {}

                    def selectionChanged(self, node, selection = (), *arg, **kw):
                        if node.leaf:
                            if hasattr(self.root, "openMethodsInNewView") and self.root.openMethodsInNewView:
                                self.session.addView(self.path + (Grimoire.Utils.Password.getasciisalt(16),), self.session.Selection
                                                     ).send.gotoPath(self.prefix + node.path, *arg, **kw)
                            else:
                                self.send.gotoPath(self.prefix + node.path, *arg, **kw)
                
                    def hoverChanged(self, node, selection = (), *arg, **kw):
                        if node.leaf:
                            self.send.hoverPath(self.prefix + node.path, *arg, **kw)

                class GenericSelection(Session.View):
                    __slots__ = ['method']
                    def __init__(self, **kw):
                        super(FormSession.GenericSelection, self).__init__(**kw)
                        self.clear()

                    def clear(self):
                        self.method = None

                    def pathToExpression(self, path):
                        if Grimoire.Utils.isInstance(path, Grimoire.Types.GrimoireReference):
                            path = self.method + path
                            if path['levels']:
                                raise ValueError("Bad reference", self.method, path['levels'], path['path'])
                            path = path['path']
                        path = list(path)
                        expr = reduce(lambda expr, member:
                         Grimoire.Utils.Serialize.Types.Extension(
                          Grimoire.Utils.Serialize.Types.Member,
                          [expr,
                           Grimoire.Utils.Serialize.Types.Extension(
                            Grimoire.Utils.Serialize.Types.Identifier,
                            member)]),
                         path,
                         Grimoire.Utils.Serialize.Types.Extension(
                          Grimoire.Utils.Serialize.Types.Identifier,
                          "_"))
                        s = StringIO.StringIO()
                        Grimoire.Utils.Serialize.Writer.write(s, expr)
                        return s.getvalue()

                    def getComposer(self, path = None, *arg, **kw):
                        if path is None: path = self.method
                        class Composer(self.session.getComposer(path, *arg, **kw)):
                            selection = self
                        return Composer

                class HoverSelection(GenericSelection):
                    def hoverSelect(self, method):
                        if self.method != method:
                            self.method = method
                            self.renderHoverSelection()

                    def renderHoverSelection(self):
                        pass

                    def hoverPath(self, path):
                        self.hoverLocation(self.pathToExpression(path))
                        
                    def hoverLocation(self, location):
                        method = self.session._.introspection.methodOfExpression(location, True)
                        self.hoverSelect(method)

                    def selectionChanged(self, method, *arg, **kw):
                        if hasattr(self.root, "openMethodsInNewView") and self.root.openMethodsInNewView:
                            self.session.addView(self.path + (Grimoire.Utils.Password.getasciisalt(16),), self.session.Selection
                                                 ).send.gotoPath(method, *arg, **kw)
                        else:
                            self.send.gotoPath(method, *arg, **kw)

                class Selection(GenericSelection):
                    __slots__ = ['params', 'result']
                        
                    def clear(self):
                        super(FormSession.Selection, self).clear()
                        self.params = None
                        self.result = None

                    def select(self, method):
                        self.clear()
                        self.method = method
                        self.params = self.session.__._getpath(
                            path=['introspection', 'params'] + list(method))()
                        if (    not Grimoire.Types.getComment(self.params)
                            and not self.params.arglist
                            and not self.params.resargstype
                            and not self.params.reskwtype):
                            self.handleCall(self.method,
                                            Grimoire.Types.getValue(self.params)())

                    def handleExecution(self, *arg, **kw):
                        self.result = self.session.handleExecution(*arg, **kw)
                        return self.result

                    def handleCall(self, method = None, args = [], handleExecution = None):
                        if method is None:
                            method = self.method
                        return self.session.handleCall(method, args, handleExecution or self.handleExecution)

                    def eval(self, expression, handleExecution = None):
                        return self.session.eval(expression, handleExecution or self.handleExecution)

                    def drawSelection(self, selection):
                        pass

                    def renderSelection(self):
                        result = Grimoire.Types.Paragraphs()
                        if self.result and not self.result.error:
                            result.append(self.result.result)
                        else:
                            if self.result and self.result.error:
                                result.append(self.result.error)
                            if self.params:
                                result.append(self.params)
                        self.drawSelection(
                            self.getComposer(self.method or ())(result))
                        
                    def gotoPath(self, path):
                        self.gotoLocation(self.pathToExpression(path))
                        
                    def gotoLocation(self, location):
                        try:
                            method = self.session._.introspection.methodOfExpression(location, True)
                        except Exception: # We've got a complex expression...
                            method = None

                        if method:
                            self.select(method)
                        else:
                            self.eval(location)
                        return self.renderSelection()

                    def applyForm(self, args):
                        self.handleCall(self.method, args)
                        self.renderSelection()
                        
                def __new__(cls, **kw):
                    sess = super(FormSession, cls).__new__(cls, **kw)
                    self = Grimoire.Types.getValue(sess)
                    self.comment = Grimoire.Types.getComment(sess)
                    return self

            return FormSession
        _call = Grimoire.Utils.cachingFunction(_call)
        def _params(self):
            return A(Ps(),
                     'Session sub-class that adds form-based client helper methods.')

    class renderable(Grimoire.Performer.Method):
        def _call(performer):
            Session = performer._getpath(Grimoire.Types.MethodBase).base()
            class RenderableSession(Session):
                class TreeView(Session.TreeView):
                    class DirCacheNode(Session.TreeView.DirCacheNode):
                        __slots__ = ['expanded']
                        def __init__(self, expanded = 0, *arg, **kw):
                            super(RenderableSession.TreeView.DirCacheNode, self).__init__(*arg, **kw)
                            self.expanded = expanded

                    def expand(self, path, depth = Grimoire.Performer.UnlimitedDepth):
                        if debugTree: print "Expand:", path, depth
                        node = self.updateDirCachePath(path, depth)
                        def expand(node, depth):
                            node.expanded = 1
                            if depth > 1:
                                for name in node.subNodes.iterkeys():
                                    expand(node.subNodes[name], depth - 1)
                        expand(self.updateDirCachePath(path, depth), depth)

                    def expandPath(self, path, depth = Grimoire.Performer.UnlimitedDepth):
                        if debugTree: print "ExpandPath:", path, depth
                        for index in xrange(0, len(path)):
                            self.expand(path[:index], 1)
                        return self.expand(path, depth)

                    def collapse(self, path):
                        if debugTree: print "Collapse:", path
                        self.updateDirCachePath(path).expanded = 0

                    def renderTree(self, renderEntry, *args, **kw):
                        def traverseEntry(node, *arg, **kw):
                            if node.expanded and not node.updated:
                                self.updateDirCache(node.path, 1, 0)
                            return renderEntry(node, *arg, **kw)
                        def renderSubEntries(node, *arg, **kw):
                            return node.expanded
                        return self.traverseTree(traverseEntry, renderSubEntries, '', *args, **kw)

                    def renderTreeToText(self):
                        pictIcon = (('[=]', '[=]'),
                                    ('\\_\\', '\\_/'))            
                        pictExpander = ((('|--', '`--'),
                                         ('|--', '`--')),
                                        (('|-+', '`-+'),
                                         ('|-.', '`-.')))
                        def renderEntry(node, sibling, res, indent=''):
                            path = node.path
                            siblings = node.parent and len(node.parent.subNodes) or 1
                            subNodes = len(node.subNodes)
                            res += indent
                            res += pictExpander[subNodes > 0 or not node.updated
                                                ][node.expanded][sibling == siblings - 1]
                            res += pictIcon[subNodes > 0][node.expanded]
                            if node.translation is not None:
                                res += node.translation
                            elif node.path:
                                res += node.path[-1]
                            else:
                                res += 'Grimoire'
                            res += "\n"
                            return (res,
                                    (indent + ['|  ', '   '][sibling == siblings - 1],),
                                    {})

                        return self.renderTree(renderEntry)

                def expand(self, *arg, **kw):
                    for view in self.views.itervalues():
                        view.send.expand(*arg, **kw)

                def expandPath(self, *arg, **kw):
                    for view in self.views.itervalues():
                        view.send.expandPath(*arg, **kw)

                def collapse(self, *arg, **kw):
                    for view in self.views.itervalues():
                        view.send.collapse(*arg, **kw)
                        
                def insertUnique(self, path, obj, **kw):
                    upath = super(RenderableSession, self).insertUnique(path, obj, **kw)
                    self.expandPath(upath, 1)
                    return upath
            
            return RenderableSession
        _call = Grimoire.Utils.cachingFunction(_call)
        def _params(self):
            return A(Ps(),
                     'Session sub-class that adds the notion of expanded and unexpanded branches, suitable for rendering a user-expandable/collapsable tree')

