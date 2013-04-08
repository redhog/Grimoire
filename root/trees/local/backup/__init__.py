import Grimoire.Performer, Grimoire.Types, types

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class unprotected_backup(Grimoire.Performer.Method):
        def _call(self):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase).load.standardtree(
                    __name__ + '._performers',
                    ['parameters'],
                    ['local', 'backup', 'initcommands']))
        def _params(self):
            return A(Ps(),
                     'Returns a backup manipulation tree for the local backup')

    class backup(Grimoire.Performer.Method):
        def _call(self, userId, password):
            if (userId != self._callWithUnlockedTree(
                    lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                        ['local', 'backup', 'login', 'username'])) or
                password != self._callWithUnlockedTree(
                    lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                        ['local', 'backup', 'login', 'password']))):
                raise Exception('Bad username or password')
            return self._callWithUnlockedTree(lambda:
                self._getpath(Grimoire.Types.MethodBase).unprotected.backup())
        def _params(self):
            return A(Ps([('userId',
                          A(types.StringType,
                            'User name')),
                         ('password',
                          A(Grimoire.Types.PasswordType,
                            'User password')),]),
                     'Log in to Returns a backup manipulation tree for the local backup')
