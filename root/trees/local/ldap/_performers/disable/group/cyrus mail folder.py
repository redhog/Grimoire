import Grimoire.Types, Grimoire.Performer, Grimoire.Utils, string, ldap

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class user(Grimoire.Performer.SubMethod):
        __path__ = ['cyrus shared mail folder', '$ldapservername']
        __related_group__ = ['group']
        def _call(self, path):
            def unlocked(path):
                conn = self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                    ['local', 'ldap', 'admin', 'conn'], cache=True)

                path = [Grimoire.Utils.encode(item, 'ascii') for item in path]

                revDnList = ['ou=People'] + ['ou=' + part for part in path]
                
                values = self._getpath(Grimoire.Types.TreeRoot,
                                       path=['directory', 'get', 'ldap'] + revDnList)

                maildirPath = values(['cn=defaults', 'grimoireCyrusdirPath'])[0].split('.')
                
                self._getpath(Grimoire.Types.MethodBase, 2,
                              ['disable', 'cyrus maildir', 'group'] + maildirPath + ['groups'] + path[:-1]
                              )(path[-1])
                
                return A(None, "Shared Cyrus mail folder disabled for group")
            return self._callWithUnlockedTree(unlocked, path)
        
        __dir_allowall__ = False
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 2,
                                      ['list', 'ldapentries', '$ldapservername', 'Groups'] + path
                                      )(depth, 'objectClass=grimoireGroup', addType='ou'))
        def _params(self, path):
            return A(Ps([]),
                     Grimoire.Types.Formattable("Disable the shared Cyrus mail folder the group %(group)s",
                                                group=Grimoire.Types.UNIXGroup(path)))
