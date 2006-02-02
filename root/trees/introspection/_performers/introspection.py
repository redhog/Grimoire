import Grimoire.Performer, Grimoire.Utils, Grimoire.Types, types


A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class dir(Grimoire.Performer.SubMethod):
        __related_group__ = ['method']
        __related_description__ = ['list', 'submethods']
        def _call(self, path, depth = Grimoire.Performer.UnlimitedDepth):
            if depth == -1:
                depth = Grimoire.Performer.UnlimitedDepth
            return self._physicalGetpath(Grimoire.Types.TreeRoot)._treeOp(path, 'dir', depth=depth)
        def _dir(self, path, depth):
            # Nyahehehe! This creates an infinite tree!
            if not path and not depth:
                return [(0, [])]
            return self._call(path, depth)
        def _params(self, path):
            return A(Ps([('depth',
                          A(types.IntType,
                            'Search depth (-1 means unlimited)')),
                         ],
                        0),
                     'List available methods')

    class objdir(Grimoire.Performer.SubMethod):
        __related_group__ = ['object']
        def _call(self, path, depth = 0, method = [], methodDepth = Grimoire.Performer.UnlimitedDepth):
            if depth == -1:
                depth = Grimoire.Performer.UnlimitedDepth
            return self._physicalGetpath(Grimoire.Types.TreeRoot)._treeOp(
                method, 'related', depth=methodDepth, objectPath=path, objectDepth=depth)
        def _dir(self, path, depth):
            return Grimoire.Utils.Map(
                lambda (leaf, objectPath, description, methodPath): (leaf, objectPath),
                self._physicalGetpath(Grimoire.Types.TreeRoot)._treeOp(
                    [], 'related',
                    depth=Grimoire.Performer.UnlimitedDepth,
                    objectPath=path, objectDepth=depth))
        def _params(self, path):
            return A(Ps([('method',
                          A(Grimoire.Types.GrimoirePath,
                            'Method(s) to limit search to')),
                         ('depth',
                          A(types.IntType,
                            'Search depth (-1 means unlimited)')),
                         ],
                        0),
                     'List methods on an object or objects for a method')

    class object(Grimoire.Performer.SubMethod):
        __related_group__ = ['object']
        def _call(self, path):
            return Grimoire.Types.AnnotatedValue(Grimoire.Types.Lines(*[Grimoire.Types.TitledURILink(self._physicalGetpath(path=path)._reference(self._physicalGetpath(Grimoire.Types.TreeRoot, path=methodPath)),
                                                                                                     Grimoire.Types.GrimoirePath(description))
                                                                        for (leaf, objectPath, description, methodPath) in self._getpath(Grimoire.Types.MethodBase, path=['objdir'] + path)() if leaf]),
                                                 Grimoire.Types.Formattable("Methods for the object %(object)s",
                                                                            object=Grimoire.Types.GrimoirePath(path)))
        def _dir(self, path, depth):
            return Grimoire.Utils.Map(
                lambda (leaf, objectPath, description, methodPath): (leaf, objectPath),
                self._physicalGetpath(Grimoire.Types.TreeRoot)._treeOp(
                    [], 'related',
                    depth=Grimoire.Performer.UnlimitedDepth,
                    objectPath=path, objectDepth=depth))
        def _params(self, path):
            return Ps()

    class related(Grimoire.Performer.SubMethod):
        __related_group__ = ['method']
        def _call(self, path):
            return Grimoire.Types.AnnotatedValue(
                Grimoire.Types.Lines(
                *[self._getpath(Grimoire.Types.MethodBase, path=['object'] + objectPath)()
                  for (leaf, objectPath, description, methodPath) in self._getpath(Grimoire.Types.MethodBase, path=['objdir'])(Grimoire.Performer.UnlimitedDepth, path, 0)]),
                Grimoire.Types.Formattable("Methods related to the method %(method)s", method=Grimoire.Types.GrimoirePath(path)))
        def _dir(self, path, depth):
            if not path and not depth:
                return [(0, [])]
            return self._getpath(Grimoire.Types.MethodBase, path=['dir'] + path)(depth)
        def _params(self, path):
            return Ps()

    class params(Grimoire.Performer.SubMethod):
        __related_group__ = ['method']
        __related_description__ = ['list', 'params']
        def _call(self, prefix):
            return self._physicalGetpath(Grimoire.Types.TreeRoot)._treeOp(prefix, 'params')
        __dir_allowall__ = False
        def _dir(self, path, depth):
            if not path and not depth:
                return [(0, [])]
            return self._getpath(Grimoire.Types.MethodBase, path=['dir'] + path)(depth)
        def _params(self, path):
            return A(Ps(),
                     'Returns a (machine readable and a human readable) description of the parameters a method takes')

    class exist(Grimoire.Performer.SubMethod):
        __related_group__ = ['method']
        __related_description__ = ['list', 'existence']
        def _call(self, prefix):
            return (1, []) in self._physicalGetpath(Grimoire.Types.TreeRoot)._treeOp(prefix, 'dir', depth=0)
        def _dir(self, path, depth):
            if not path and not depth:
                return [(0, [])]
            return self._getpath(Grimoire.Types.MethodBase, path=['dir'] + path)(depth)
        def _params(self, path):
            return A(Ps(),
                     'Determines wethever a method exists in the tree or not')

    class able(Grimoire.Performer.SubMethod):
        __related_group__ = ['method']
        __related_description__ = ['list', 'ability']
        def _call(self, prefix, effective = False):
            if effective and self._unlockedTree():
                return True
            try:
                return self._physicalGetpath(Grimoire.Types.TreeRoot)._ability()(prefix)
            except AttributeError:
                return True
        def _dir(self, path, depth):
            return [(1, [])]
        def _params(self, path):
            return A(Ps(),
                     'Determines wethever the current user is allowd to perform a method with a specific name (regardless of the existence of such a method)')
