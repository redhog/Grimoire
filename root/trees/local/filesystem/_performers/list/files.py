import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, string, types, stat, os

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

modeNumbers = [A(1, 'Directories'),
               A(2, 'Character devices'),
               A(4, 'Block devices'),
               A(8, 'Regular files'),
               A(16, 'Fifo:s'),
               A(32, 'Symbolic links'),
               A(64, 'Sockets')]

  
allModes = 2 ** len(modeNumbers) - 1


class Performer(Grimoire.Performer.Base):
    class files(Grimoire.Performer.SubMethod):
        __path__ = ['files', '$fileservername']
        def _call(self, path, depth = Grimoire.Performer.UnlimitedDepth,
                  what = allModes, convertToDirList = True):
            dpth = depth
            if dpth == -1:
                dpth = Grimoire.Performer.UnlimitedDepth
            basePath = Grimoire.Types.defaultLocalRoot + self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                    ['local', 'filesystem', 'basepath'], [])) + path
            basePathLen = len(basePath)
            def modeTolocal(mode):
                if (stat.S_ISDIR(mode)):
                    return 1
                elif (stat.S_ISCHR(mode)):
                    return 2
                elif (stat.S_ISBLK(mode)):
                    return 4
                elif (stat.S_ISREG(mode)):
                    return 8
                elif (stat.S_ISFIFO(mode)):
                    return 16
                elif (stat.S_ISLNK(mode)):
                    return 32
                elif (stat.S_ISSOCK(mode)):
                    return 64
                else:
                    return 0

            def listtree(path, dpth):
                paths = []
                upath = unicode(path)
                try:
                    mode = os.stat(upath).st_mode
                    if (modeTolocal(mode) & what) !=0 :
                        paths.append((True, path))
                    if stat.S_ISDIR(mode):
                         paths.append((False, path))
                         if dpth:
                             for name in os.listdir(upath):
                                 paths.extend(listtree(path + [name], dpth - 1))
                except OSError:
                    pass
                return paths
            def manglePath((leaf, path)):
                relative = path['relative'][basePathLen:]
                if convertToDirList:
                    return (leaf, list(relative))
                elif leaf:
                    return unicode(relative)
                raise Grimoire.Utils.FilterOutError
            return Grimoire.Utils.Map(manglePath, listtree(basePath, dpth))
        def _dir(self, path, depth):
            return [(1, [])]
        def _params(self, path):
            return A(Ps([('what',
                          A(Grimoire.Types.BitfieldType.derive(types.IntType, modeNumbers),
                            "What to list")),
                         ('convertToDirList',
                          A(Grimoire.Types.BooleanType,
                            "Convert entry listing to a Grimoire directory listing (that is, reverse and split paths at '/')")),
                         ]),
                     Grimoire.Types.Formattable(
                         'List files and directories entries under %(path)s',
                         path=Grimoire.Types.LocalPath(path)))
