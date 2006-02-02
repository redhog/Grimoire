import Grimoire.Utils, Grimoire.Performer, Grimoire.Types, types, os, StringIO

class Performer(Grimoire.Performer.Base):
    class file(Grimoire.Performer.SubMethod):
        __related_group__ = ['file']
        __path__ = ['file', '$fileservername']
        def _call(self, path):
            root = Grimoire.Types.defaultLocalRoot + self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                    ['local', 'filesystem', 'basepath'], []))
            dstPath = unicode(root + path)
            if os.path.islink(dstPath):
                os.remove(dstPath)
            else:
                for root, dirs, files in os.walk(dstPath, topdown=False):
                    for name in files:
                        os.remove(os.path.join(root, name))
                    for name in dirs:
                        path = os.path.join(root, name)
                        if os.path.islink(path):
                            os.remove(path)
                        else:
                            os.rmdir(path)
                os.rmdir(dstPath)
            return Grimoire.Types.AnnotatedValue(None, 'File or directory successfully removed')
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 1,
                                      ['list', 'files', '$fileservername'] + path)(depth, 1))
        def _params(self, path):
            root = Grimoire.Types.defaultLocalRoot + self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                    ['local', 'filesystem', 'basepath'], []))
            return Grimoire.Types.AnnotatedValue(
                Grimoire.Types.ParamsType.derive(),
                Grimoire.Types.Formattable(
                    'Remove the file or directory %(destination)s',
                    destination=root + path))
