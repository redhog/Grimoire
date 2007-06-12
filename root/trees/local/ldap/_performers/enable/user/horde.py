import Grimoire.Types, Grimoire.Performer, Grimoire.Utils, string, ldap

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class user(Grimoire.Performer.SubMethod):
        __path__ = ['horde', '$ldapservername']
        __related_group__ = ['user']
        def _call(self, path):
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
                    'attrlist': ['objectClass']}
            res = conn.result(conn.search(**args))
            objectClasses = list(res[1][0][1]['objectClass'])
            mod = False
            if 'hordePerson' not in objectClasses:
                objectClasses.append('hordePerson')
                mod = True
            if 'top' not in objectClasses:
                objectClasses.append('top')
                mod = True
            if mod:
                conn.modify_s(baseDn, [(ldap.MOD_REPLACE, 'objectClass', objectClasses)])
            else:
                return A(None, "Horde web interface already enabled for account")
            return A(None, "Horde web interface enabled for account")
        __dir_allowall__ = False                     
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 2,
                                      ['list', 'ldapentries', '$ldapservername', 'People'] + path
                                      )(depth, filter = 'uid=*', addType = 'ou', endType = 'uid'))
        def _params(self, path):
            return A(Ps([]), Grimoire.Types.Formattable("Enable Horde web interface for the user %(username)s",
                                                        username=path[-1]))
