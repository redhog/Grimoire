import Grimoire.Performer, Grimoire.Types.Ability, Grimoire.Types, types

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class login(Grimoire.Performer.Method):
        def _call(self, description, tree):
            directory = self._callWithUnlockedTree(lambda: self._getpath(Grimoire.Types.TreeRoot).directory.new())
            directory.directory.set.treeinfo(['local', 'login', 'description'], description)
            directory.directory.set.treeinfo(['local', 'login', 'tree'], tree)
            return Grimoire.Performer.Restrictor(
                Grimoire.Performer.Composer(
                    Grimoire.Performer.Prefixer(['introspection'], self._callWithUnlockedTree(lambda: self._getpath(Grimoire.Types.TreeRoot).trees.introspection())),
                    directory,
                    self._callWithUnlockedTree(lambda: self._getpath(Grimoire.Types.MethodBase).load(__name__ + '._performers'))),
                Grimoire.Types.Ability.List([(Grimoire.Types.Ability.Allow, ['login']),
                                       (Grimoire.Types.Ability.Allow, ['introspection'])]))
        def _params(self):
            return A(Ps([('description',
                          A(types.UnicodeType,
                            "Description")),
                         ('tree',
                          A(Grimoire.Performer.Performer,
                            "login method"))],
                        2),
                     'Wraps any method that accepts at least the two parameters username and password into one that accepts only those, presenting the user with a nicely-looking login-screen')
