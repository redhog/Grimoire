import Grimoire.Performer, Grimoire.Types

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class login(Grimoire.Performer.Method):
        def _call(self, userId, password):
            return Grimoire.Performer.Logical(
                self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.treeinfo(
                    ['local', 'login', 'tree']))(userId, password))
        def _params(self):
            description = self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.treeinfo(
                    ['local', 'login', 'description']))
            return A(Ps([('userId',
                          A(Grimoire.Types.UsernameType,
                            "Username")),
                         ('password',
                          A(Grimoire.Types.PasswordType,
                            "Password")),
                         ]),
                     Grimoire.Types.Lines(
                         'Welcome to Grimoire!',
                         Grimoire.Types.Formattable(
                             'Please enter your username and password to log in to %(description)s',
                             description = description)))

