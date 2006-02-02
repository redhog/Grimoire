import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, string, ldap

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class directory_implementation_get_user(Grimoire.Performer.SubMethod):
        def _call(self, path):
            if not path or path[0] != Grimoire.Types.pathSeparator:
                raise AttributeError(path)
            path = path[1:]
            def unlocked():
                userId = self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(['local', 'sql', 'user', 'id'])
                if path == ['language']:
                    return self._getpath(Grimoire.Types.MethodBase,
                                         path=['list', 'nonpath', '$sqlentries', '$sqlservername']
                                         )(['users'], [['language']], where = """"id" = '%s'""" % userId,
                                           prettyPrint = False)[0][0][1]
                raise AttributeError(path)
            return self._callWithUnlockedTree(unlocked)
        def _params(self, path):
            return A(Ps(),
                     Grimoire.Types.Formattable(
                         'Read the %(attribute)s of the current user',
                         Types.Reducible(path[1:], ' ')))
        __dir_allowall__ = False
        def _dir(self, path, depth):
            if not depth:
                if (not path or
                    path[0] != Grimoire.Types.pathSeparator):
                    return []
                try:
                    self._call(path)
                    return [(1, [])]
                except AttributeError:
                    return []
            # FIXME: Not quite implemented yet, huh?
            return []
