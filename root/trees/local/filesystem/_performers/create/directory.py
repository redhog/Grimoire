import Grimoire.Utils, Grimoire.Performer, Grimoire.Types, types, os, os.path, stat, errno

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

if hasattr(os, 'lstat'):
    statFn = os.lstat
else:
    statFn = os.stat

if hasattr(os, 'lchown'):
    chownFn = os.lchown
else:
    chownFn = os.chown


class Performer(Grimoire.Performer.Base):
    class path(Grimoire.Performer.SubMethod):
        __related_group__ = ['directory']
        __path__ = ['path', '$fileservername']
        def _call(self, path, mode = None, uid = None, gid = None):
            if uid is None: uid = -1
            if gid is None: gid = -1
            def createDirs(path):
                pathStr = unicode(path)
                if not os.path.isdir(pathStr):
                    if not path['relative']:
                        raise IOError(errno.ENOTDIR, 'Bad drive specification')
                    createDirs(path[:-1])
                    os.mkdir(pathStr)
                    if mode is not None:
                        os.chmod(pathStr, int(mode))
                    if uid != -1 or gid != -1:
                        chownFn(pathStr, uid, gid)
            createDirs(Grimoire.Types.defaultLocalRoot + self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                    ['local', 'filesystem', 'basepath'], [])) + path)
            return Grimoire.Types.AnnotatedValue(None,
                                                 'Created')
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 1,
                                      ['list', 'files', '$fileservername'] + path)(depth, 1))

        def _params(self, path):
            return A(Ps([('mode',
                          A(Grimoire.Types.BitfieldType.derive(
                              types.IntType,
                              [A(stat.S_ISUID, 'Set UID on execution'),
                               A(stat.S_ISGID, 'Set GID on execution/propagation owner of directory to items in it'),
                               A(stat.S_ISVTX, 'Only owner or owner of item can can rename/delete items in directory'),
                               A(stat.S_IRUSR, 'Owner has read permission'),
                               A(stat.S_IWUSR, 'Owner has write permission'),
                               A(stat.S_IXUSR, 'Owner has execute permission'),
                               A(stat.S_IRGRP, 'Group has read permission'),
                               A(stat.S_IWGRP, 'Group has write permission'),
                               A(stat.S_IXGRP, 'Group has execute permission'),
                               A(stat.S_IROTH, 'Others has read permission'),
                               A(stat.S_IWOTH, 'Others has write permission'),
                               A(stat.S_IXOTH, 'Others has execute permission'),
                               ]),
                            'File mode')),
                         ('uid', A(types.IntType, 'Numerical user ID')),
                         ('gid', A(types.IntType, 'Numerical user homegroup ID')),
                         ],
                        0),
                     Grimoire.Types.Formattable(
                         'Create the directory %(destination)s',
                         destination=Grimoire.Types.LocalPath(path)))

    class directory(Grimoire.Performer.SubMethod):
        __related_group__ = ['directory']
        __path__ = ['directory', '$fileservername']
        def _call(self, path, name, mode = None, uid = None, gid = None):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, path=['path', '$fileservername'] + path + [name]
                                      )(mode, uid, gid))

        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 1,
                                      ['list', 'files', '$fileservername'] + path)(depth, 1))

        def _params(self, path):
            return A(Ps([('name', A(types.UnicodeType, 'Directory to create')),
                         ('mode',
                          A(Grimoire.Types.BitfieldType.derive(
                              types.IntType,
                              [A(stat.S_ISUID, 'Set UID on execution'),
                               A(stat.S_ISGID, 'Set GID on execution/propagation owner of directory to items in it'),
                               A(stat.S_ISVTX, 'Only owner or owner of item can can rename/delete items in directory'),
                               A(stat.S_IRUSR, 'Owner has read permission'),
                               A(stat.S_IWUSR, 'Owner has write permission'),
                               A(stat.S_IXUSR, 'Owner has execute permission'),
                               A(stat.S_IRGRP, 'Group has read permission'),
                               A(stat.S_IWGRP, 'Group has write permission'),
                               A(stat.S_IXGRP, 'Group has execute permission'),
                               A(stat.S_IROTH, 'Others has read permission'),
                               A(stat.S_IWOTH, 'Others has write permission'),
                               A(stat.S_IXOTH, 'Others has execute permission'),
                               ]),
                            'File mode')),
                         ('uid', A(types.IntType, 'Numerical user ID')),
                         ('gid', A(types.IntType, 'Numerical user homegroup ID')),
                         ],
                        0),
                     Grimoire.Types.Formattable(
                         'Create a directory at %(destination)s',
                         destination=Grimoire.Types.LocalPath(path)))

