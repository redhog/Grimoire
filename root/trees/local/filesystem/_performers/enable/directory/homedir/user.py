import Grimoire.Utils, Grimoire.Performer, Grimoire.Types, types, os, StringIO

class Performer(Grimoire.Performer.Base):
    class homedir_user(Grimoire.Performer.SubMethod):
        __related_group__ = ['directory']
        __path__ = ['user', '$fileservername']
        def _call(self, path, name, homeGroup, uid = None, gid = None, **variables):
            def unlocked():
                base = Grimoire.Types.defaultLocalRoot + self._callWithUnlockedTree(
                    lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                    ['local', 'filesystem', 'basepath'], []))

                homedirPath = base + path + ['group.users'] + name
                homedirPathStr = unicode(homedirPath)
                if os.access(unicode(homedirPath), os.F_OK):
                    Grimoire.Utils.lchown(unicode(homedirPath), uid, gid)
                    if os.access(unicode(homedirPath + ['.grimoireSavedAccess']), os.F_OK):
                        f = open(unicode(homedirPath + ['.grimoireSavedAccess']), 'r')
                        savedAccess = dict([(key, int(value))
                                            for (key, value)
                                            in [line.strip().split('=',2)
                                                for line
                                                in f.xreadlines()]])
                        f.close()
                        
                        os.chmod(homedirPathStr, savedAccess['mode'])
                else:
                    self._getpath(Grimoire.Types.MethodBase, 3,
                                  ['create', 'copy from skeleton'] + ['$fileservername'] + path + ['group.users']
                                  )(name, uid = uid, gid = gid, skel=['skel'], **variables)

                    self._getpath(Grimoire.Types.MethodBase, 3,
                                  ['create', 'directory'] + ['$fileservername'] + path + ['group.users', name]
                                  )('shared', uid=0, gid=0)

                    self._getpath(Grimoire.Types.MethodBase, 3,
                                  ['create', 'symlink'] + ['$fileservername'] + path + ['group.users', name, 'shared']
                                  )(homeGroup, path + ['group.contents'], uid=0, gid=0)

                return Grimoire.Types.AnnotatedValue(
                    None,
                    'Successfully created home directory')

            return self._callWithUnlockedTree(unlocked)

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
