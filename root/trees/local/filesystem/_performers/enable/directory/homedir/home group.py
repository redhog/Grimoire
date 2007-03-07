import Grimoire.Utils, Grimoire.Performer, Grimoire.Types, types, os, StringIO

class Performer(Grimoire.Performer.Base):
    class homedir_homegroup(Grimoire.Performer.SubMethod):
        __related_group__ = ['directory']
        __path__ = ['home group', '$fileservername']
        def _call(self, path, gid = None, **variables):
            def unlocked():
                self._getpath(Grimoire.Types.MethodBase, 3, ['create', 'directory'] + ['$fileservername'] + path[:-1]
                              )(path[-1], uid=0, gid=0)
                self._getpath(Grimoire.Types.MethodBase, 3, ['create', 'copy from skeleton'] + ['$fileservername'] + path
                              )('group.contents', gid = gid, skel=['groupskel'], **variables)
                self._getpath(Grimoire.Types.MethodBase, 3, ['create', 'directory'] + ['$fileservername'] + path
                              )('group.users', uid=0, gid=0)
            self._callWithUnlockedTree(unlocked)
            return Grimoire.Types.AnnotatedValue(
                None,
                'Successfully created home group directory')

        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._physicalGetpath(Grimoire.Types.MethodBase,
                                              path=['directory', '$fileservername'] + path
                                              )._treeOp([], 'dir', depth=depth))
        def _params(self, path):
            return Grimoire.Types.AnnotatedValue(
                Grimoire.Types.ParamsType.derive(
                    [('gid',
                      Grimoire.Types.AnnotatedValue(types.IntType,
                                                    'Numerical user homegroup ID')),
                     ],
                    0),
                Grimoire.Types.Formattable(
                    'Enable a home-directory for the home group %(group)s',
                    group=Grimoire.Types.defaultLocalRoot + path))
