import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, os, types

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class DirectorySubMethod(Grimoire.Performer.SubMethod):
    def _dir(self, path, depth):
        # dict.keys just to get unique entries, or otherwize we would
        # get a zillion of equal ones...
        return Grimoire.Utils.Map(
            lambda (leaf, path): (leaf, Grimoire.Utils.splitList(path, Grimoire.Types.pathSeparator, 2)[0]),
            self._getpath(Grimoire.Types.TreeRoot,
                          path=['introspection', 'dir'] +  self._physicalGetpath(Grimoire.Types.MethodBase, 0, ['implementation', 'get'] + path)._pathForSelf()
                          )(depth))

class NoDefault: pass

class Performer(Grimoire.Performer.Base):
    class get(DirectorySubMethod):
        _getCache = {}
        def _call(self, path, keypath, default = NoDefault, setDefault = True, all = False, cache = False):
            if cache:
                tupleKeypath = tuple(keypath)
                if tupleKeypath not in self._getCache:
                    self._getCache[tupleKeypath] = {}
                def get(prefix):
                    if prefix in self._getCache[tupleKeypath]:
                        return self._getCache[tupleKeypath][prefix]
                    if prefix:
                        results = get(prefix[:-1])
                    else:
                        results = []
                    try:
                        results += [self._getpath(Grimoire.Types.MethodBase,
                                                  path=list(('implementation', 'get') + prefix + (Grimoire.Types.pathSeparator,) + tupleKeypath))()]
                    except (AttributeError, TypeError), e:
                        pass
                    self._getCache[tupleKeypath][prefix] = results
                    return results
                results = get(tuple(path))
                if not all and results:
                    return results[0]
            else:
                results = []
                for prefix in Grimoire.Utils.Prefixes(path):
                    try:
                        results.append(self._getpath(Grimoire.Types.MethodBase,
                                                     path=['implementation', 'get'] + prefix + [Grimoire.Types.pathSeparator] + keypath)())
                        if not all:
                            return results[0]
                    except (AttributeError, TypeError):
                        pass
            
            if all:
                return results
            if default == NoDefault:
                raise AttributeError(path, keypath)
            if setDefault:
                self._getpath(Grimoire.Types.MethodBase, path=['set'] + path)(keypath, default)
            return default
        def _params(self, path):
            return A(Ps([('keypath', A(Grimoire.Types.StringListType,
                                       'Path to the configuration value')),
                         ('default', A(Grimoire.Types.AnyType,
                                       'Default value')),
                         ('setDefault', A(Grimoire.Types.BooleanType,
                                          'Set the parameter to the default value too (not just return it) if no value is found')),
                         ('cache', A(Grimoire.Types.BooleanType,
                                     'Cache values at all levels in the tree, and use such cached values when doing the lookup'))
                         ],
                        1),
                     'Read a configuration value')

    class set(DirectorySubMethod):
        def _call(self, path, keypath, value):
            self._getpath(Grimoire.Types.MethodBase,
                          path = ['implementation', 'set'] + path + [Grimoire.Types.pathSeparator] + keypath
                          )(value)
            return A(None, 'Successfully set value')
        def _params(self, path):
            return A(Ps([('keypath', A(Grimoire.Types.StringListType,
                                       'Path to the configuration value')),
                         ('value', A(Grimoire.Types.AnyType,
                                     'Value to set'))]),
                     'Set a configuration value')

    class list(DirectorySubMethod):
        def _call(self, path, depth = Grimoire.Performer.UnlimitedDepth, recursive = 1):
            subDepth = depth
            if subDepth == -1:
                subDepth = Grimoire.Performer.UnlimitedDepth
            keys = []
            for pathPrefix in [[path], Grimoire.Utils.Prefixes(path)][recursive]:
                try:
                    keys += self._getpath(Grimoire.Types.TreeRoot,
                                          path=['introspection', 'dir'] + self._physicalGetpath(
                                              Grimoire.Types.MethodBase, 0,
                                              ['implementation', 'get'] + pathPrefix + [Grimoire.Types.pathSeparator]
                                              )._pathForSelf()
                                          )(subDepth)
                except (AttributeError, TypeError):
                    pass
            return keys
        def _params(self, path):
            return A(Ps([('depth',
                          A(types.IntType,
                            'Search depth (-1 means unlimited)')),
                         ('recursive',
                          A(Grimoire.Types.BooleanType,
                            'Show inherited keypaths'))],
                        0),
                     'List configuration keys')

    class new(Grimoire.Performer.Method):
        def _call(self):
            return Grimoire.Performer.Logical(
                Grimoire.Performer.Composer(
                    *[Grimoire.Performer.Prefixer(
                         ['directory', 'implementation'],
                         self._getpath(Grimoire.Types.MethodBase, path = ['implementation', 'new'] + path)())
                      for (leaf, path) in self._getpath(Grimoire.Types.TreeRoot,
                                                        path=['introspection', 'dir'] + self._physicalGetpath(Grimoire.Types.MethodBase, 0,
                                                                                                              ['implementation', 'new'])._pathForSelf()
                                                        )()] +
                     [Grimoire.Performer.Prefixer(['directory', 'implementation'],
                                                  Grimoire.Performer.Isolator(self._getpath(Grimoire.Types.MethodBase).implementation)),
                      Grimoire.Performer.Prefixer(['directory'], self._physicalBase().__class__())]))
        def _params(self):
            return A(Ps(),
                     'Create a new tree')
