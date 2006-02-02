import Grimoire.Utils, Grimoire.Performer, Grimoire.Types, types, os, StringIO

class Performer(Grimoire.Performer.Base):
    class symlink(Grimoire.Performer.SubMethod):
        __related_group__ = ['directory']
        __path__ = ['symlink', '$fileservername']
        def _call(self, path, name, source, uid, gid):
            root = Grimoire.Types.defaultLocalRoot + self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                    ['local', 'filesystem', 'basepath'], []))
            dstPath = unicode(root + path + [name])
            srcPath = unicode(root + source)
            os.symlink(srcPath, dstPath)
            os.lchown(dstPath, uid, gid)
            return Grimoire.Types.AnnotatedValue(
                None,
                "Symbolic link successfully created")
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._physicalGetpath(Grimoire.Types.MethodBase,
                                              path=['directory', '$fileservername'] + path
                                              )._treeOp([], 'dir', depth=depth))
        def _params(self, path):
            root = Grimoire.Types.defaultLocalRoot + self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                    ['local', 'filesystem', 'basepath'], []))
            return Grimoire.Types.AnnotatedValue(
                Grimoire.Types.ParamsType.derive(
                    [('name',
                      Grimoire.Types.AnnotatedValue(types.UnicodeType,
                                                    'Name of symbolic link')),
                     ('source',
                      Grimoire.Types.AnnotatedValue(Grimoire.Types.UnicodeListType,
                                                    'Path to source file (the symlink will point at this file)')),
                     ('uid',
                      Grimoire.Types.AnnotatedValue(types.IntType,
                                                    'Numerical user ID')),
                     ('gid',
                      Grimoire.Types.AnnotatedValue(types.IntType,
                                                    'Numerical user homegroup ID')),
                     ],
                    4),
                Grimoire.Types.Formattable(
                    'Create a symbolic link at %(destination)s',
                    destination=root + path))
