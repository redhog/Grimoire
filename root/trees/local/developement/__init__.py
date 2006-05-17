import Grimoire.Performer, Grimoire.Types, types, Fixme

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class unprotected_developement(Grimoire.Performer.Method):
        def _call(self):
            directory = self._callWithUnlockedTree(lambda: self._getpath(Grimoire.Types.TreeRoot).directory.new())
            setParam = directory.directory.set.parameters
            getParam = directory.directory.get.parameters

            projectPath = Grimoire.Types.defaultLocalRoot + self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                    ['local', 'developement', 'basepath'], []))
            setParam(['local', 'developement', 'fixmes'], Fixme.Fixmes(unicode(projectPath)))
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase).load.standardtree(
                    __name__ + '._performers',
                    ['parameters'],
                    ['local', 'developement', 'initcommands'],
                    directory = directory))
        def _params(self):
            return A(Ps(),
                     'Returns a developement manipulation tree for the local developement')

    class developement(Grimoire.Performer.Method):
        def _call(self, userId, password):
            if (userId != self._callWithUnlockedTree(
                    lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                        ['local', 'developement', 'login', 'username'])) or
                password != self._callWithUnlockedTree(
                    lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                        ['local', 'developement', 'login', 'password']))):
                raise Exception('Bad username or password')
            return self._callWithUnlockedTree(lambda:
                self._getpath(Grimoire.Types.MethodBase).unprotected.developement())
        def _params(self):
            return A(Ps([('userId',
                          A(types.StringType,
                            'User name')),
                         ('password',
                          A(Grimoire.Types.PasswordType,
                            'User password')),]),
                     'Log in to Returns a developement manipulation tree for the local developement')
