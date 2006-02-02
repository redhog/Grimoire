import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, types, ldap, string

class Performer(Grimoire.Performer.Base):
    class user_memberships(Grimoire.Performer.SubMethod):
        __path__ = ['user', 'memberships', '$ldapservername']
        def _call(self, path):
            return Grimoire.Utils.Map(
                lambda (x, y): y,
                self._callWithUnlockedTree(
                    lambda: self._getpath(Grimoire.Types.MethodBase, path=['ldapentries', '$ldapservername', 'Groups']
                                          )(Grimoire.Performer.UnlimitedDepth,
                                            '(& (ou=*) (memberUid=%s))' % path[-1],
                                            addType='ou')))
        __dir_allowall__ = False
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase,
                                      path=['ldapentries', '$ldapservername', 'People'] + path
                                      )(depth,
                                        '(& (objectClass=posixAccount) (objectClass=sambaSamAccount))', addType='ou', endType = 'uid'))
        def _params(self, path):
            return Grimoire.Types.ParamsType.derive()
