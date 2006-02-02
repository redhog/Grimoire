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
            return Grimoire.Types.AnnotatedValue(
                Grimoire.Types.getValue(
                    self._callWithUnlockedTree(
                        lambda: self._getpath(Grimoire.Types.TreeRoot,
                                              path=['introspection', 'params'] + self._physicalGetpath(
                                                  Grimoire.Types.MethodBase, 1,
                                                  ['password', '$ldapservername' ] + self.__getUserPath()
                                                  )._pathForSelf()
                                              )())),
                'Change your own password')
