import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, string, types, stat, os

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class files(Grimoire.Performer.SubMethod):
        __path__ = ['files', '$backupservername']
        def _call(self, path, depth = Grimoire.Performer.UnlimitedDepth):
            if depth == -1: depth = Grimoire.Performer.UnlimitedDepth
            backupRootPath = Grimoire.Types.defaultLocalRoot + self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                    ['local', 'backup', 'path', 'backup'], []))
            backupDataPath = backupRootPath + 'rdiff-backup-data'
            backupIncrementsPath = backupDataPath + 'increments'

            def listTree(root, path, depth, exist, isdir, listdir):
                results = []
                fullpath = root + path
                if exist(fullpath):
                    results.append((True, path))
                if isdir(fullpath):
                    if depth:
                        for name in listdir(fullpath):
                            results.extend(listTree(root, path + [name], depth - 1, exist, isdir, listdir))
                    else:
                        results.append((False, path))
                return results

            def realExist(path):
                return os.access(unicode(path), os.F_OK)
            def realIsdir(path):
                try:
                    return stat.S_ISDIR(os.stat(unicode(path)).st_mode)
                except OSError:
                    return False
            def realListdir(path):
                results = set()
                for name in os.listdir(unicode(path)):
                    if name == 'rdiff-backup-data': continue
                    results.add(name)
                return results
            def incrementExist(path):
                if os.access(unicode(path), os.F_OK): return True
                if not os.access(unicode(path[:-1]), os.F_OK): return False
                for name in os.listdir(unicode(path[:-1])):
                    if name.startswith(path[-1]) and name.rsplit('.', 3)[0] == path[-1]:
                        return True
                return False
            def incrementIsdir(path):
                try:
                    return stat.S_ISDIR(os.stat(unicode(path)).st_mode)
                except OSError:
                    return False
            def incrementListdir(path):
                results = set()
                for name in os.listdir(unicode(path)):
                    if stat.S_ISDIR(os.stat(unicode(path + name)).st_mode):
                        results.add(name)
                    elif name.endswith('.diff.gz'):
                        results.add(name.rsplit('.', 3)[0])
                return results

            return (listTree(backupRootPath + path, [], depth, realExist, realIsdir, realListdir) +
                    listTree(backupIncrementsPath + path, [], depth, incrementExist, incrementIsdir, incrementListdir))
        def _dir(self, path, depth):
            return self._call(path, depth)
        def _params(self, path):
            return A(Ps([('depth',
                          Grimoire.Types.AnnotatedValue(
                              types.IntType,
                              "Only return entries this far down in the tree (-1 means infinity)")),
                         ]),
                     Grimoire.Types.Formattable(
                         'List files and directories entries under %(path)s',
                         path=Grimoire.Types.LocalPath(path)))
