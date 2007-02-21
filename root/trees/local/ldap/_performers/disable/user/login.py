import Grimoire.Types, Grimoire.Performer, Grimoire.Utils, string, ldap

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class user(Grimoire.Performer.SubMethod):
        __path__ = ['login', '$ldapservername']
        __related_group__ = ['user']
        def _call(self, path):
            # set password to !password
            conn = self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot
                                      ).directory.get.parameters(['local', 'ldap', 'admin', 'conn'],
                                                                 cache=True))
            oupath = [ "ou="+elem for elem in path[:-1]]
            # Add 'ou' or 'uid' to all parts of the path
            baseDn = string.join(Grimoire.Utils.Reverse(['ou=People'] + oupath + ["uid="+path[-1]]) + [conn.realm], ',')
            args = {'base': baseDn,
                    'scope': ldap.SCOPE_BASE,
                    'filterstr': 'uid=*',
                    'attrlist': ['userPassword',
                                 'sambaAcctFlags',
                                 'loginShell']}
            res = conn.result(conn.search(**args))
            # Disable the users password
            up = res[1][0][1]['userPassword'][0]
            if up[0] == "!":
                return A(None, "Account already disabled")
            else:
                up = "!"+up
            # Also, set the login shell to /bin/false
            # (and save the original later on the row)
            ls = '/bin/false '+res[1][0][1]['loginShell'][0]
            
            # Set the samba account disabled
            af = res[1][0][1]['sambaAcctFlags'][0]
            daf = af[0:2]+'D'+af[3:]

            conn.modify_s(baseDn, [(ldap.MOD_REPLACE, 'userPassword', up)])
            conn.modify_s(baseDn, [(ldap.MOD_REPLACE, 'loginShell', ls)])
            conn.modify_s(baseDn, [(ldap.MOD_REPLACE, 'sambaAcctFlags', daf)])
            
            return A(None, "Account disabled for logins")
        __dir_allowall__ = False                     
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 2,
                                      ['list', 'ldapentries', '$ldapservername', 'People'] + path
                                      )(depth, filter = 'uid=*', addType = 'ou', endType = 'uid'))
        def _params(self, path):
            return A(Ps([]),
                     Grimoire.Types.Formattable("Disable the account of the user %(username)s",
                                                username=path[-1]))
