import Grimoire.Types, Grimoire.Performer, Grimoire.Utils, string, ldap

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class user(Grimoire.Performer.SubMethod):
        __path__ = ['homedir', '$ldapservername']
        __related_group__ = ['user']
        def _call(self, path):
            def unlocked(path):
                conn = self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                    ['local', 'ldap', 'admin', 'conn'], cache=True)

                path = [Grimoire.Utils.encode(item, 'ascii') for item in path]

                groupPath = path[:-1]
                user = path[-1]

                revGroupDnList = ['ou=People'] + ['ou=' + part for part in groupPath]

                groupDnList = [item for item in revGroupDnList]
                groupDnList.reverse()
                
                dnList = ['uid=' + user] + groupDnList
                dn = string.join(dnList + [conn.realm], ',')


                uidNumber = self._getpath(Grimoire.Types.TreeRoot,
                                          path=['directory', 'get', 'ldap'] + revGroupDnList + ['uid=' + user]
                                          )(['uidNumber'])[0]

                gidNumber = self._getpath(Grimoire.Types.TreeRoot,
                                          path=['directory', 'get', 'ldap'] + revGroupDnList + ['uid=' + user]
                                          )(['gidNumber'])[0]

                values = self._getpath(Grimoire.Types.TreeRoot,
                                       path=['directory', 'get', 'ldap'] + revGroupDnList)

                root = Grimoire.Types.defaultLocalRoot
                clientHomedirPath = values(['cn=defaults', 'grimoireClientHomedirPath'], 'home.people', False)[0].split('.')
                homedirPath = values(['cn=defaults', 'grimoireHomedirPath'])[0].split('.')

                homeDirectory = Grimoire.Utils.encode(root + clientHomedirPath + groupPath + ['group.users', user], 'ascii')


                self._getpath(Grimoire.Types.MethodBase, 2,
                              ['enable', 'directory', 'homedir', 'user'] + homedirPath + groupPath
                              )(user,
                                homeGroup = unicode(Grimoire.Types.UNIXGroup(['people'] + groupPath)),
                                uid = int(uidNumber),
                                gid = int(gidNumber),
                                USER=user,
                                HOME=homeDirectory)
                
                return A(None, "Home directory enabled for account")
            return self._callWithUnlockedTree(unlocked, path)
        
        __dir_allowall__ = False                     
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 2,
                                      ['list', 'ldapentries', '$ldapservername', 'People'] + path
                                      )(depth, filter = 'uid=*', addType = 'ou', endType = 'uid'))
        
        def _params(self, path):
            return A(Ps([]),
                     Grimoire.Types.Formattable("Enable a home-directory for the user %(username)s",
                                                username=path[-1]))
