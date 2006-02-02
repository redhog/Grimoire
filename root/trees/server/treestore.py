import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, Grimoire.Utils.Password, os, types

debugUnregister = 0

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive


class RegisteredTree:
    def __init__(self, tree):
        self.key = Grimoire.Utils.Password.getasciisalt(16)
        self.tree = tree
        self.usage = 1

class TreeStore(Grimoire.Performer.Base):
    def __init__(self, *arg, **kw):
        Grimoire.Performer.Base.__init__(self, *arg, **kw)
        self._trees = {}
        self._users = {}
        self._currentUser = Grimoire.Utils.ThreadLocalData()

    class register_user(Grimoire.Performer.Method):
        def _call(self):
            user = Grimoire.Utils.Password.getasciisalt(16)
            self._physicalBase()._users[user] = []
            return A(user,
                     'You have been registered with the user/connection ID')
        def _params(self):
            return PS()

    class set_thread_user(Grimoire.Performer.Method):
        def _call(self, user):
            self._physicalBase()._currentUser.set(user)
        def _params(self):
            return A(PS([('user',
                          A(types.StringType,
                            'ID of the user of this tree (the calling process or connection)'))]),
                     'Set the (default) user for the current thread')

    class unregister_user(Grimoire.Performer.Method):
        def _call(self, user = None):
            parent = self._physicalBase()
            usr = user or parent._currentUser.get()
            for tree in parent._users[usr]:
                if debugUnregister: print "Unregister ", usr, ":", tree.key, tree.tree
                tree.usage -= 1
                if tree.usage < 1:
                    if debugUnregister: print "Deleting ", usr, ":", tree.key, tree.tree
                    del parent._trees[tree.key]
            del parent._users[usr]
        def _params(self):
            return A(PS([('user',
                          A(types.StringType,
                            'ID of the user of this tree (the calling process or connection)'))],
                        0),
                     'Unregister a user (or the current user)')
        
    class register_tree(Grimoire.Performer.Method):
        def _call(self, tree = None, key = None, user = None):
            parent = self._physicalBase()
            usr = user or parent._currentUser.get()
            if key:
                if tree:
                    raise Exception('Only one of key and tree may be specified') 
                tree = parent._trees[key]
                parent._users[usr].append(tree)
                tree.usage += 1
                return A(None, 'Tree successfully re-registered')
            else:
                if not tree:
                    raise Exception('Either of key and tree must be specified') 
                tree = RegisteredTree(tree)
                parent._users[usr].append(tree)
                parent._trees[tree.key] = tree
                return A(tree.key,
                         'The tree got registred with the key')
        def _params(self):
            return A(PS([('tree',
                          A(Grimoire.Performer.Performer,
                            'The tree to register')),
                         ('key',
                          A(types.StringType,
                            'The key of an already registered tree to re-register with another user')),
                         ('user',
                          A(types.StringType,
                            'ID of the user of this tree (the calling process or connection)'))],
                        0),
                     'Register a Grimoire tree in the tree-store')

    class unregister_tree(Grimoire.Performer.Method):
        def _call(self, key, user = None):
            parent = self._physicalBase()
            usr = user or parent._currentUser.get()
            tree = parent._trees[key]
            parent._users[usr].remove(tree)
            if debugUnregister: print "Unregister ", usr, ":", tree.key, tree.tree
            tree.usage -= 1
            if tree.usage < 1:
                if debugUnregister: print "Deleting ", usr, ":", tree.key, tree.tree
                del parent._trees[key]
            return A(None,
                     'The tree was successfully unregistered')
        def _params(self):
            return A(PS([('key',
                          A(types.StringType,
                            'The key of the tree to unregister')),
                         ('user',
                          A(types.StringType,
                            'ID of the user of this tree (the calling process or connection)'))],
                        1),
                     'Unregister a Grimoire tree from the tree-store')

    class call(Grimoire.Performer.Physical):
        # Bypass all that fluffy submethod-shit and implement it all by ourselves...
        def _treeOp_recurse(self, path, **kw):
            if not path or path[0] not in self._physicalBase()._trees:
                # Security by severe obscurity - can you guess a _random_ 16-char key-string?
                raise Grimoire.Types.MethodNotImplementedHere
            return self._physicalBase()._trees[path[0]].tree._treeOp_recurse(path=path[1:], **kw)

class Performer(Grimoire.Performer.Base):
    class treestore(Grimoire.Performer.Method):
        def _call(self):
            return TreeStore()
        def _params(self):
            return PS()
