import Grimoire.Types, Grimoire.Performer, Grimoire.Utils, string, ldap

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class user(Grimoire.Performer.SubMethod):
        __path__ = ['cyrus mail folder', '$ldapservername']
        __related_group__ = ['user']
        def _call(self, path):
            def unlocked(path):
                conn = self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                    ['local', 'ldap', 'admin', 'conn'], cache=True)

                path = [Grimoire.Utils.encode(item, 'ascii') for item in path]

                groupPath = path[:-1]
                user = path[-1]

                revGroupDnList = ['ou=People'] + ['ou=' + part for part in groupPath]
                
                values = self._getpath(Grimoire.Types.TreeRoot,
                                       path=['directory', 'get', 'ldap'] + revGroupDnList)

                maildirPath = values(['cn=defaults', 'grimoireMaildirPath'])[0].split('.')

                self._getpath(Grimoire.Types.MethodBase, 2,
                              ['enable', 'cyrus maildir', 'user'] + maildirPath + groupPath
                              )(user)
                
                return A(None, "Cyrus mail folder enabled for user")
            return self._callWithUnlockedTree(unlocked, path)
        
        __dir_allowall__ = False                     
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 2,
                                      ['list', 'ldapentries', '$ldapservername', 'People'] + path
                                      )(depth, filter = 'uid=*', addType = 'ou', endType = 'uid'))
        
        def _params(self, path):
            return A(Ps([]),
                     Grimoire.Types.Formattable("Enable a Cyrus mail folder for the user %(username)s",
                                                username=path[-1]))
