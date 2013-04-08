import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, types, os

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class fixmes(Grimoire.Performer.SubMethod):
        __path__ = ['fixmes', '$fileservername']
        __related_group__ = ['code', 'fixmes']
        __dir_allowall__ = False
        def _call(self, path, *arg, **kw):
            fixmes = self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(['local', 'developement', 'fixmes'], cache=True))

        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, levels=1, path=['list', 'fixmedir', '$fileservername'] + path)(
                    depth,
                    fixmesAreMethods = True, fieldsAreMethods = True,
                    hideFields = ()))
        def _params(self, path):
            fixmes = self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(['local', 'developement', 'fixmes'], cache=True))
            name=path[0]
            fixme = fixmes.fixmes[name]
            if len(path) == 1:
                comment = Grimoire.Types.Formattable('Change the fixme %(name)s', name=name)
                fields = fixme.fields.iterkeys()
            elif len(path) == 3:
                fields = [path[2]]
                comment = Grimoire.Types.Formattable('Change %(field)s of the fixme %(name)s', field=path[2], name=name)
            else:
                assert(false)
            return A(Ps([(field, A(Grimoire.Types.HintedType.derive(type(fixme.fields[field]), [fixme.fields[field]]),
                                   field))
                         for field in fields]),
                     comment)
