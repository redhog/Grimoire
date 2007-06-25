import Grimoire.Types, Grimoire.Performer, Grimoire.Utils, string, ldap, base64

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class user(Grimoire.Performer.SubMethod):
        __path__ = ['freebusy', '$ldapservername']
        __related_group__ = ['user']
        def _call(self, path):
            conn = self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot
                                      ).directory.get.parameters(['local', 'ldap', 'admin', 'conn'],
                                                                 cache=True))
            user = Grimoire.Utils.encode(path[-1], 'ascii')
            oupath = ['ou=People'] + [ "ou="+elem for elem in path[:-1]]
            # Add 'ou' or 'uid' to all parts of the path
            baseDn = string.join(Grimoire.Utils.Reverse(oupath + ["uid="+user]) + [conn.realm], ',')
            args = {'base': baseDn,
                    'scope': ldap.SCOPE_BASE,
                    'filterstr': 'uid=*',
                    'attrlist': ['objectClass']}
            res = conn.result(conn.search(**args))

            objectClasses = res[1][0][1]['objectClass']
            if 'kolabInetOrgPerson' not in objectClasses:
                conn.modify_s(baseDn, [(ldap.MOD_REPLACE,
                                        'objectClass',
                                        objectClasses + ['kolabInetOrgPerson'])])
                
            values = self._getpath(Grimoire.Types.TreeRoot,
                                   path=['directory', 'get', 'ldap'] + oupath)
            maildirPath = values(['cn=defaults', 'grimoireCyrusdirPath'])[0].split('.')
            self._getpath(Grimoire.Types.MethodBase, 2,
                          ['enable', 'freebusy', 'user'] + maildirPath + oupath
                          )(user)

            return A(None, "Free/busy collection enabled for account")
        __dir_allowall__ = False                     
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 2,
                                      ['list', 'ldapentries', '$ldapservername', 'People'] + path
                                      )(depth, filter = 'uid=*', addType = 'ou', endType = 'uid'))
        def _params(self, path):
            return A(Ps([]),
                     Grimoire.Types.Formattable("Enable free/busy information collection / generation for %(username)s",
                                                username=path[-1]))
