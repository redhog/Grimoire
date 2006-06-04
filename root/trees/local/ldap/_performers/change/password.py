import Grimoire.Utils, Grimoire.Utils.Password, Grimoire.Performer, Grimoire.Types

class Performer(Grimoire.Performer.Base):
    class password(Grimoire.Performer.SubMethod):
        __path__ = ['password', '$ldapservername']
        __related_group__ = ['user']
        def _call(self, path, newpwd):
            import string, ldap
            newpwd = Grimoire.Utils.encode(newpwd, 'ascii')
            path = Grimoire.Utils.Reverse(path)
            conn = self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                    ['local', 'ldap', 'admin', 'conn'], cache=True))
            dn = string.join(['uid=' + path[0]] + map(lambda x: 'ou=' + x, path[1:]), ',') + ',ou=People,' + conn.realm
            
            lmpwd, ntpwd = self._callWithUnlockedTree(
                lambda: getattr(self._getpath(Grimoire.Types.MethodBase, 1).create.ntpassword,
                                '$ldapservername')(newpwd))
            conn.modify_s(dn, [(ldap.MOD_REPLACE, "sambaLMPassword", lmpwd),
                               (ldap.MOD_REPLACE, "sambaNTPassword", ntpwd),
                               (ldap.MOD_REPLACE, "userPassword", "{SSHA}" + Grimoire.Utils.Password.sshaencrypt(newpwd))])
            return Grimoire.Types.AnnotatedValue(None, 'Password successfully changed')
        __dir_allowall__ = False
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 1,
                                      ['list', 'ldapentries', '$ldapservername', 'People'] + path
                                      )(depth,
                                        '(& (objectClass=posixAccount) (objectClass=sambaSamAccount))', addType='ou', endType='uid'))
        def _params(self, path):
            import base64
            return Grimoire.Types.AnnotatedValue(
                Grimoire.Types.ParamsType.derive(
                    [('newpwd',
                      Grimoire.Types.AnnotatedValue(
                          Grimoire.Types.HintedType.derive(Grimoire.Types.NewPasswordType,
                                                    [base64.encodestring(Grimoire.Utils.Password.getsalt())
                                                     for x in range(0, 3)]),
                          "New password to set"))]),
                Grimoire.Types.Formattable(
                    'Change password for user %(path)s',
                    path=Grimoire.Types.GrimoirePath(path)))
