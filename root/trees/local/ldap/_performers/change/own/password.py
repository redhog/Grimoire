import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, types

class Performer(Grimoire.Performer.Base):
    class password(Grimoire.Performer.Method):
        __path__ = ['password', '$ldapservername']
        def __getUserPath(self):
            # [1:] to remove ou=People
            return map(lambda item: item.split('=')[1],
                       Grimoire.Utils.Reverse(
                           self._callWithUnlockedTree(
                               lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                                   ['local', 'ldap', 'user', 'dn']).split(','))
                           )[1:])
        def _call(self, newpwd):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 1,
                              ['password', '$ldapservername'] + self.__getUserPath()
                                      )(newpwd))
        def _params(self):
            #### fixme ####
            # description = """We'd like to use introspection.params,
            # but that bugs when that tree and our tree have different
            # roots and change.password is hidden in the real tree..."""
            #### end ####
            def unlocked():
                return Grimoire.Types.AnnotatedValue(
                    Grimoire.Types.getValue(
                        self._physicalGetpath(
                            Grimoire.Types.TreeRoot
                            )._treeOp(
                                self._physicalGetpath(
                                    Grimoire.Types.MethodBase, 1,
                                    ['password', '$ldapservername'] + self.__getUserPath()
                                    )._pathForSelf(),
                                'params')),
                    'Change your own password')
            return self._callWithUnlockedTree(unlocked)
