import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, types, os

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class fixmes(Grimoire.Performer.SubMethod):
        __path__ = ['fixmes', '$fileservername']
        __related_group__ = ['code', 'fixmes']
        __dir_allowall__ = False
        def _call(self, path):
            fixmes = self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(['local', 'developement', 'fixmes'], cache=True))
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, levels=1, path=['list', 'fixmedir', '$fileservername'] + path)(
                    depth,
                    fixmesAreMethods = True, fieldsAreMethods = True,
                    hideFields = ()))
        def _params(self, path):
            if len(path) == 1:
                return A(Ps(),
                         Grimoire.Types.Formattable('Change the fixme %(name)s', name=path[0]))
            elif len(path) == 3:
                return A(Ps(),
                         Grimoire.Types.Formattable('Change %(field)s of the fixme %(name)s', field=path[2], name=path[0]))
            assert(false);
