import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, types, ldap, string

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class user(Grimoire.Performer.SubMethod):
        __path__ = ['user', '$ldapservername']
        def _call(self, path):
            dn = ['ou=People'] + [ 'ou='+elem for elem in path[0:-1]] + [ 'uid='+path[-1]]
            def unlocked():
                for group in self._getpath(Grimoire.Types.MethodBase, 1,
                                           ['list', 'user', 'memberships', '$ldapservername'] + path)():
                    self._getpath(Grimoire.Types.MethodBase, 1,
                                  ['change', 'group', 'removeMember', '$ldapservername'] + group)(path[-1])
                return self._getpath(Grimoire.Types.MethodBase, path=['ldapentry'] + dn)()
            return self._callWithUnlockedTree(unlocked)
        __dir_allowall__ = False                                       
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 1,
                                      ['list', 'ldapentries', '$ldapservername', 'People'] + path
                                      )(-1, filter = 'uid=*', addType = 'ou', endType = 'uid'))
        def _params(self, path):
            return A(Ps([]), Grimoire.Types.Formattable("Permanently delete the account of the user %(username)s", username=path[-1]))
