import Grimoire.Utils, Grimoire.Performer, Grimoire.Types, types, os, stat

class Performer(Grimoire.Performer.Base):
    class homedir_user(Grimoire.Performer.SubMethod):
        __related_group__ = ['directory']
        __path__ = ['user', '$fileservername']
        def _call(self, path, user):
            def unlocked():
                base = Grimoire.Types.defaultLocalRoot + self._callWithUnlockedTree(
                    lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                    ['local', 'filesystem', 'basepath'], []))

                homedirPath = base + path + ['group.users'] + user
                homedirPathStr = unicode(homedirPath)

                if os.access(homedirPathStr, os.F_OK):
                    oldStat = Grimoire.Utils.lstat(homedirPathStr)
                    oldMode = stat.S_IMODE(oldStat.st_mode)

                    Grimoire.Utils.lchown(homedirPathStr, 0, 0)
                    os.chmod(homedirPathStr, stat.S_IRWXU)

                    f = open(unicode(homedirPath + ['.grimoireSavedAccess']), 'w')
                    f.write("""uid=%(uid)s
gid=%(gid)s
mode=%(mode)s
""" % {'uid':oldStat.st_uid,
       'gid':oldStat.st_gid,
       'mode':str(stat.S_IMODE(oldStat.st_mode))})
                    f.close()

                return Grimoire.Types.AnnotatedValue(
                    None,
                    'Successfully disabled home directory')

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
                          "Name of copy to create"))
                     ]),
                Grimoire.Types.Formattable(
                    'Disable an existing home-directory %(path)s',
                    path=Grimoire.Types.LocalPath(path)))
