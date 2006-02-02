import Grimoire.Types.Ability, Grimoire.Performer, Grimoire.Types, Grimoire.root.trees.local.ldap._Ldap, Grimoire.root.trees.local.ldap._Ability
import Grimoire.Utils, ldap, types, sys, traceback

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class ldap(Grimoire.Performer.Method):
        def _call(self, userId, password, server = None, realm = None, admindn = None, adminpwd = None):
            directory = self._callWithUnlockedTree(lambda: self._getpath(Grimoire.Types.TreeRoot).directory.new())
            setParam = directory.directory.set.parameters
            getParam = directory.directory.get.parameters
            
            if server: setParam(['local', 'ldap', 'server'], server)
            rServer = getParam(['local', 'ldap', 'server'], 'ldap')

            if realm: setParam(['local', 'ldap', 'realm'], realm)
            rRealm = getParam(['local', 'ldap', 'realm'], 'dc=jamtlinux,dc=net')

            if admindn: setParam(['local', 'ldap', 'admin', 'dn'], admindn)
            rAdmindn = getParam(['local', 'ldap', 'admin', 'dn'], 'cn=admin')

            if adminpwd: setParam(['local', 'ldap', 'admin', 'password'], adminpwd)
            try:
                rAdminpwd = getParam(['local', 'ldap', 'admin', 'password'])
            except AttributeError:
                raise Exception('No valid LDAP admin password supplied')

            conn = ldap.open(rServer)
            conn.realm = rRealm
            conn.server = rServer

            userdn = userId
            if userId.find(',') == -1:
                id = conn.search('ou=People,' + rRealm, ldap.SCOPE_SUBTREE, 'uid=%s' % userId, attrlist=['dn'])
                res = conn.result(id)[1]
                if len(res) == 0: raise ldap.INVALID_CREDENTIALS("You don't exist, go away")
                userdn = res[0][0][:-len(rRealm) - 1]
            setParam(['local', 'ldap', 'user', 'dn'], userdn)

            try:
                conn.simple_bind_s(userdn + ',' + rRealm, Grimoire.Utils.encode(password, 'ascii'))
            except ldap.INVALID_CREDENTIALS:
                raise ldap.INVALID_CREDENTIALS("You don't exist, go away")
            except ldap.UNWILLING_TO_PERFORM:
                raise ldap.UNWILLING_TO_PERFORM("An empty password is not allowed")
            setParam(['local', 'ldap', 'user', 'conn'], conn)

            # Admconn connected as ADMIN
            admconn = ldap.open(rServer)
            admconn.realm = rRealm
            admconn.server = rServer
            admconn.simple_bind_s(rAdmindn + ',' + rRealm, Grimoire.Utils.encode(rAdminpwd, 'ascii'))
            setParam(['local', 'ldap', 'admin', 'conn'], admconn)

            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase).load.standardtree(
                    __name__ + '._performers',
                    ['ldap'] + Grimoire.Utils.Reverse(userdn.split(',')),
                    ['cn=defaults', 'grimoireInitCommand'],
                    Grimoire.root.trees.local.ldap._Ability.LdapList(userdn, admconn),
                    directory))

        def _params(self):
            return A(Ps([('userId',
                          A(Grimoire.Types.UsernameType,
                            'User name')),
                         ('password',
                          A(Grimoire.Types.PasswordType,
                            'User password')),
                         ('server',
                          A(types.StringType,
                            'LDAP server name')),
                         ('realm',
                          A(types.StringType,
                            'LDAP realm (base DN appended to all DNs)')),
                         ('admindn',
                          A(types.StringType,
                            'LDAP administrator DN (relative to realm))')),
                         ('adminpwd',
                          A(Grimoire.Types.PasswordType,
                            'Administrator password')),
                         ],
                        2),
                     'Returns an LDAP manipulation tree for an LDAP server')

