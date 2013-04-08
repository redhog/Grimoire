import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, string, types, stat, os

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class versions(Grimoire.Performer.SubMethod):
        __path__ = ['versions', '$backupservername']
        def _call(self, path):
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

            result = []

            if os.access(unicode(backupRootPath + path), os.F_OK):
                if stat.S_ISDIR(os.stat(unicode(backupRootPath + path)).st_mode):
                    return backups
                else:
                    result.append(current)
            if os.access(unicode(backupIncrementsPath + path), os.F_OK):
                if stat.S_ISDIR(os.stat(unicode(backupIncrementsPath + path)).st_mode):
                    return backups
            if os.access(unicode(backupIncrementsPath + path[:-1]), os.F_OK):
                if stat.S_ISDIR(os.stat(unicode(backupIncrementsPath + path[:-1])).st_mode):
                    for name in os.listdir(unicode(backupIncrementsPath + path[:-1])):
                        if name.startswith(path[-1]) and name.endswith('.diff.gz'):
                             result.append(name.rsplit('.', 3)[1])
            return result

        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase,
                                      path = ['files', '$backupservername'] + path)(depth))
        def _params(self, path):
            returnPs()
