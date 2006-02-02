import Grimoire.Types.Ability, Grimoire.Performer, Grimoire.Types, types, Grimoire.Utils.Serialize.RPC

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive


class IDTreeBinding(Grimoire.Utils.Wrapper):
    def __init__(self, binding, id):
        Grimoire.Utils.Wrapper.__init__(self, binding)
        self.__dict__['id'] = id

    def call(self, **kw):
        return self.value._call(self.id, **kw)
    
    def __del__(self):
        self.value.remove(self.id)

class TreeBinding(Grimoire.Utils.Serialize.RPC.StdObjectMappedBinding):
    def __init__(self, tree = None, *arg, **kw):
        Grimoire.Utils.Serialize.RPC.StdObjectMappedBinding.__init__(self, *arg, **kw)
        self.tree = Grimoire.Performer.Physical(tree)
        self.id = None

    def registerObject(self, obj):
        if self.tree is None:
            raise NotImplemented
        return Grimoire.Types.getValue(
            self.tree._treeOp(['treestore', 'register', 'tree'], 'call', callarg=(obj,), callkw={}))
    
    def setup(self, requestHandler):
        if self.tree is None:
            raise NotImplemented
        self.user = Grimoire.Types.getValue(
            self.tree._treeOp(['treestore', 'register', 'user'], 'call', callarg=(), callkw={}))

    def finish(self, requestHandler):
        if self.tree is None:
            raise NotImplemented
        self.tree._treeOp(['treestore', 'unregister', 'user'], 'call', callarg=(self.user,), callkw={})

    def dispatch(self, path, wholePath, **kw):
        if self.tree is None:
            raise NotImplemented
        self.tree._treeOp(['treestore', 'set', 'thread', 'user'], 'call', callarg=(self.user,), callkw={})
        return self.tree._treeOp_recurse(path=path, wholePath=path, **kw)

    def call(self, **kw):
        return self._call('public', **kw)

    def _call(self, id, path, **kw):
        return Grimoire.Utils.Serialize.RPC.StdObjectMappedBinding.call(self, path=['treestore', 'call', id] + path, **kw)

    def new(self, id):
        return IDTreeBinding(self, id)

    def remove(self, id):
        pass
        #Grimoire.Utils.Serialize.RPC.StdObjectMappedBinding.call(self, ['treestore', 'unregister', 'tree'], id)


class Performer(Grimoire.Performer.Base):
    class dirt(Grimoire.Performer.Method):
        def _call(self):
            paramsAbility = self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(['rpc', 'serialization'], None)
            class Binding(TreeBinding):
                def __init__(self, tree = None, ability = None, *arg, **kw):
                    TreeBinding.__init__(
                        self, tree = tree,
                        ability = ability or paramsAbility or Grimoire.Types.Ability.List([
                            (Grimoire.Types.Ability.Allow, ['Grimoire', 'Types']),
                            (Grimoire.Types.Ability.Allow, ['Grimoire', 'About']),
                            ]),
                        *arg, **kw)
            return Binding
        def _params(self, path):
            return A(Ps(),
                     'Construct a DIRT binding for a tree')
