import Grimoire.Utils, Grimoire.Performer, Grimoire.Types, types

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class file(Grimoire.Performer.SubMethod):
        __related_group__ = ['file']
        __path__ = ['file', '$backupservername']
        __dir_allowall__ = False        
        def _call(self, path, name = None):
            systemRootPath = Grimoire.Types.defaultLocalRoot + self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                    ['local', 'backup', 'path', 'system'], []))
            backupRootPath = Grimoire.Types.defaultLocalRoot + self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                    ['local', 'backup', 'path', 'backup'], []))
            restoreTime = path[-1]
            path = path[:-2] # path[-2] is the string 'Restore'...
            dstpath = path
            if name is not None:
                if dstpath:
                    dstpath = dstpath[:-1]
                dstpath = dstpath + [name]
            out, err = Grimoire.Utils.system('rdiff-backup', ['rdiff-backup',
                                                              '-r', restoreTime,
                                                              unicode(backupRootPath + path),
                                                              unicode(systemRootPath + dstpath)
                                                              ], onlyOkStatus = True)
            return A(None,
                     "Files restored")
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 1,
                                      ['list', 'files', '$backupservername'] + path)(depth))
        def _params(self, path):
            return A(Ps([('name',
                          A(types.UnicodeType, 'Save restored copy under this name')),
                         ],
                        0),
                     Grimoire.Types.Formattable(
                         'Restore %(destination)s to the state it was in at %(time)s',
                         destination=Grimoire.Types.defaultLocalRoot + path[:-2],
                         time=path[-1]))
