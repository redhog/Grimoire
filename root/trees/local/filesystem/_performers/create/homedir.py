import Grimoire.Utils, Grimoire.Performer, Grimoire.Types, types, os, StringIO

class Performer(Grimoire.Performer.Base):
    class homedir_user(Grimoire.Performer.SubMethod):
        __related_group__ = ['directory']
        __path__ = ['homedir', 'user', '$fileservername']
        def _call(self, path, name, homeGroup, uid = None, gid = None, **variables):
            def unlocked():
                self._getpath(Grimoire.Types.MethodBase, path=['copy from skeleton'] + ['$fileservername'] + path + ['group.users']
                              )(name, gid = gid, skel=['skel'], **variables)
                self._getpath(Grimoire.Types.MethodBase, path=['directory'] + ['$fileservername'] + path + ['group.users', name]
                              )('shared', uid=0, gid=0)
                self._getpath(Grimoire.Types.MethodBase, path=['symlink'] + ['$fileservername'] + path + ['group.users', name, 'shared']
                              )(homeGroup, path + ['group.contents'], uid=0, gid=0)
            self._callWithUnlockedTree(unlocked)
            return Grimoire.Types.AnnotatedValue(
                None,
                'Successfully created home directory')

        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._physicalGetpath(Grimoire.Types.MethodBase,
                                              path=['directory', '$fileservername'] + path
                                              )._treeOp([], 'dir', depth=depth))
        def _params(self, path):
            return Grimoire.Types.AnnotatedValue(
                Grimoire.Types.ParamsType.derive(
                    [('name',
                      Grimoire.Types.AnnotatedValue(
                          types.UnicodeType,
                          "Name of copy to create")),
                     ('uid',
                      Grimoire.TypessrcPath.AnnotatedValue(types.IntType,
                                                    'Numerical user ID')),
                     ('gid',
                      Grimoire.Types.AnnotatedValue(types.IntType,
                                                    'Numerical user homegroup ID')),
                     ],
                    1),
                Grimoire.Types.Formattable(
                    'Create a new home-directory in %(group)s',
                    group=Grimoire.Types.LocalPath(path)))

    class homedir_homegroup(Grimoire.Performer.SubMethod):
        __related_group__ = ['directory']
        __path__ = ['homedir', 'homegroup', '$fileservername']
        def _call(self, path, name, gid = None, **variables):
            def unlocked():
                self._getpath(Grimoire.Types.MethodBase, path=['directory'] + ['$fileservername'] + path
                              )(name, uid=0, gid=0)
                self._getpath(Grimoire.Types.MethodBase, path=['copy from skeleton'] + ['$fileservername'] + path + [name]
                              )('group.contents', gid = gid, skel=['groupskel'], **variables)
                self._getpath(Grimoire.Types.MethodBase, path=['directory'] + ['$fileservername'] + path + [name]
                              )('group.users', uid=0, gid=0)
            self._callWithUnlockedTree(unlocked)
            return Grimoire.Types.AnnotatedValue(
                None,
                'Successfully created group directory')

        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._physicalGetpath(Grimoire.Types.MethodBase,
                                              path=['directory', '$fileservername'] + path
                                              )._treeOp([], 'dir', depth=depth))
        def _params(self, path):
            return Grimoire.Types.AnnotatedValue(
                Grimoire.Types.ParamsType.derive(
                    [('name',
                      Grimoire.Types.AnnotatedValue(
                          types.UnicodeType,
                          "Name of copy to create")),
                     ('gid',
                      Grimoire.Types.AnnotatedValue(types.IntType,
                                                    'Numerical user homegroup ID')),
                     ],
                    1),
                Grimoire.Types.Formattable(
                    'Create a new homegroup-directory in %(group)s',
                    group=Grimoire.Types.LocalPath(path)))

    class homedir_group(Grimoire.Performer.SubMethod):
        __related_group__ = ['directory']
        __path__ = ['homedir', 'group', '$fileservername']
        def _call(self, path, name, gid = None, **variables):
            def unlocked():
                self._getpath(Grimoire.Types.MethodBase, path=['directory'] + ['$fileservername'] + path
                              )(name, uid=0, gid=0)
                self._getpath(Grimoire.Types.MethodBase, path=['copy from skeleton'] + ['$fileservername'] + path + [name]
                              )('group.contents', gid = gid, skel=['groupskel'], **variables)
            self._callWithUnlockedTree(unlocked)
            return Grimoire.Types.AnnotatedValue(
                None,
                'Successfully created group directory')

        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._physicalGetpath(Grimoire.Types.MethodBase,
                                              path=['directory', '$fileservername'] + path
                                              )._treeOp([], 'dir', depth=depth))
        def _params(self, path):
            return Grimoire.Types.AnnotatedValue(
                Grimoire.Types.ParamsType.derive(
                    [('name',
                      Grimoire.Types.AnnotatedValue(
                          types.UnicodeType,
                          "Name of copy to create")),
                     ('gid',
                      Grimoire.Types.AnnotatedValue(types.IntType,
                                                    'Numerical user homegroup ID')),
                     ],
                    1),
                Grimoire.Types.Formattable(
                    'Create a new group-directory in %(group)s',
                    group=Grimoire.Types.LocalPath(path)))

    class maildir_user(Grimoire.Performer.SubMethod):
        __related_group__ = ['directory']
        __path__ = ['maildir', 'user', '$fileservername']
        def _call(self, path, name, uid = None, gid = None, **variables):
            def unlocked():
                self._getpath(Grimoire.Types.MethodBase, path=['directory'] + ['$fileservername'] + path + ['group.users']
                              )(name, uid=uid, gid=gid)
                for part in ('new', 'cur', 'tmp'):
                    self._getpath(Grimoire.Types.MethodBase, path=['directory'] + ['$fileservername'] + path + ['group.users', name]
                                  )(part, uid=uid, gid=gid)
            self._callWithUnlockedTree(unlocked)
            return Grimoire.Types.AnnotatedValue(
                None,
                'Successfully created home directory')

        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._physicalGetpath(Grimoire.Types.MethodBase,
                                              path=['directory', '$fileservername'] + path
                                              )._treeOp([], 'dir', depth=depth))
        def _params(self, path):
            return Grimoire.Types.AnnotatedValue(
                Grimoire.Types.ParamsType.derive(
                    [('name',
                      Grimoire.Types.AnnotatedValue(
                          types.UnicodeType,
                          "Name of copy to create")),
                     ('uid',
                      Grimoire.TypessrcPath.AnnotatedValue(types.IntType,
                                                    'Numerical user ID')),
                     ('gid',
                      Grimoire.Types.AnnotatedValue(types.IntType,
                                                    'Numerical user homegroup ID')),
                     ],
                    1),
                Grimoire.Types.Formattable(
                    'Create a new mail-directory in %(group)s',
                    group=Grimoire.Types.LocalPath(path)))

    class maildir_homegroup(Grimoire.Performer.SubMethod):
        __related_group__ = ['directory']
        __path__ = ['maildir', 'homegroup', '$fileservername']
        def _call(self, path, name, gid = None, **variables):
            def unlocked():
                self._getpath(Grimoire.Types.MethodBase, path=['directory'] + ['$fileservername'] + path
                              )(name, uid=0, gid=0)
                self._getpath(Grimoire.Types.MethodBase, path=['directory'] + ['$fileservername'] + path + [name]
                              )('group.users', uid=0, gid=0)
            self._callWithUnlockedTree(unlocked)
            return Grimoire.Types.AnnotatedValue(
                None,
                'Successfully created group directory')

        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._physicalGetpath(Grimoire.Types.MethodBase,
                                              path=['directory', '$fileservername'] + path
                                              )._treeOp([], 'dir', depth=depth))
        def _params(self, path):
            return Grimoire.Types.AnnotatedValue(
                Grimoire.Types.ParamsType.derive(
                    [('name',
                      Grimoire.Types.AnnotatedValue(
                          types.UnicodeType,
                          "Name of copy to create")),
                     ('gid',
                      Grimoire.Types.AnnotatedValue(types.IntType,
                                                    'Numerical user homegroup ID')),
                     ],
                    1),
                Grimoire.Types.Formattable(
                    'Create a new mailgroup-directory in %(group)s',
                    group=Grimoire.Types.LocalPath(path)))

    class maildir_group(Grimoire.Performer.SubMethod):
        __related_group__ = ['directory']
        __path__ = ['maildir', 'group', '$fileservername']
        def _call(self, path, name, gid = None, **variables):
            return Grimoire.Types.AnnotatedValue(
                None,
                'Successfully created group directory')

        def _dir(self, path, depth):
            return []
        def _params(self, path):
            return Grimoire.Types.AnnotatedValue(
                Grimoire.Types.ParamsType.derive(
                    [('name',
                      Grimoire.Types.AnnotatedValue(
                          types.UnicodeType,
                          "Name of copy to create")),
                     ('gid',
                      Grimoire.Types.AnnotatedValue(types.IntType,
                                                    'Numerical group ID')),
                     ],
                    1),
                Grimoire.Types.Formattable(
                    'Create a new group-directory in %(group)s',
                    group=Grimoire.Types.LocalPath(path)))
