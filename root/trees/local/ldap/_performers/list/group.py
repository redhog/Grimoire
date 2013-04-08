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

    class group_memberships(Grimoire.Performer.SubMethod):
        __path__ = ['group', 'memberships', '$ldapservername']
        def _call(self, path):
            def unlocked():
                conn = self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                    ['local', 'ldap', 'admin', 'conn'], cache=True)
                dnpath = ['ou=Groups'] + ['ou=' + item for item in path]
                dn = unicode(Grimoire.Types.DN([conn.realm] + dnpath))
                id = conn.search(scope = ldap.SCOPE_BASE, attrlist = ['memberUid'], base = dn)
                res = conn.result(id)[1][0][1]
                if 'memberUid' not in res: return []
                return res['memberUid']
            return self._callWithUnlockedTree(unlocked)

        __dir_allowall__ = False
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, path = ['ldapentries', '$ldapservername', 'Groups'] + path
                                      )(depth, 'ou=*', addType='ou'))
        def _params(self, path):
            return Grimoire.Types.ParamsType.derive()
