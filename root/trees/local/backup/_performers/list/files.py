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

            backups = set([])
            for name in os.listdir(unicode(backupDataPath)):
                if name.startswith('current_mirror'):
                    current = name.split('.')[1]
                    backups.add(current)
                elif name.startswith('mirror_metadata'):
                    backups.add(name.split('.')[1])

            def listTree(root, path, depth, exist, isdir, listdir, listversions, topplevel = True):
                results = []
                fullpath = root + path
                if len(fullpath) > 2 and fullpath[-2] == 'Restore' and exist(fullpath[:-2], fullpath[-1]):
                    results.append((True, path))
                elif isdir(fullpath):
                    if depth:
                        if topplevel:
                            # This is done "one level up" in the loop
                            # belowlistdir below, but for the
                            # toplevel, there is no "one level up", so
                            # we have to do it ourselves...
                            for version in listversions(fullpath):
                                results.append((True, path + ['Restore', version]))
                        for name, (dir, versions) in listdir(fullpath).iteritems():
                            for version in versions:
                                results.append((True, path + [name, 'Restore', version]))
                            if dir:
                                results.extend(listTree(root, path + [name], depth - 1, exist, isdir, listdir, listversions, False))
                    else:
                        results.append((False, path))
                else:
                    if fullpath[-1] == 'Restore':
                        for version in listversions(fullpath[:-1]):
                            results.append((True, path + [version]))
                    else:
                        for version in listversions(fullpath):
                            results.append((True, path + ['Restore', version]))
                return results

            def realExist(path, version):
                if version not in backups: return False
                if version == current: return os.access(unicode(path), os.F_OK)
                try:
                    return stat.S_ISDIR(os.stat(unicode(path)).st_mode)
                except OSError:
                    return False
            def realIsdir(path):
                try:
                    return stat.S_ISDIR(os.stat(unicode(path)).st_mode)
                except OSError:
                    return False
            def realListdir(path):
                results = {}
                for name in os.listdir(unicode(path)):
                    if name == 'rdiff-backup-data': continue
                    if stat.S_ISDIR(os.stat(unicode(path + name)).st_mode):
                        results[name] = (True, set(backups))
                    else:
                        results[name] = (False, set([current]))
                return results
            def realListversions(path):
                if realIsdir(unicode(path)):
                    return backups
                elif os.access(unicode(path), os.F_OK):
                    return [current]
                return []
            def incrementExist(path, version):
                if version not in backups: return False
                if path and os.access(unicode(path[:-1] + (path[-1] + '.' + version + '.diff.gz')), os.F_OK): return True
                try:
                    return stat.S_ISDIR(os.stat(unicode(path)).st_mode)
                except OSError:
                    return False
            def incrementIsdir(path):
                try:
                    return stat.S_ISDIR(os.stat(unicode(path)).st_mode)
                except OSError:
                    return False
            def incrementListdir(path):
                results = {}
                for name in os.listdir(unicode(path)):
                    if stat.S_ISDIR(os.stat(unicode(path + name)).st_mode):
                        results[name] = (True, set(backups))
                    elif name.endswith('.diff.gz'):
                        name, version, = name.rsplit('.', 3)[:2]
                        if name not in results:
                            results[name] = (False, set())
                        results[name][1].add(version)
                return results
            def incrementListversions(path):
                if incrementIsdir(unicode(path)):
                    return backups
                if incrementIsdir(path[:-1]):
                    dirlist = incrementListdir(path[:-1])
                    if path[-1] in dirlist:
                        return dirlist[path[-1]][1]
                return []

            return (listTree(backupRootPath + path, [], depth, realExist, realIsdir, realListdir, realListversions) +
                    listTree(backupIncrementsPath + path, [], depth, incrementExist, incrementIsdir, incrementListdir, incrementListversions))
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
