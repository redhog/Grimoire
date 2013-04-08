import Grimoire.Types, Grimoire.Performer, Grimoire.Utils, string, ldap

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class group(Grimoire.Performer.SubMethod):
        __path__ = ['homedir', '$ldapservername']
        __related_group__ = ['group']
        def _call(self, path):
            def unlocked(path):
                path = [Grimoire.Utils.encode(item, 'ascii') for item in path]

                revDnList = ['ou=Groups'] + ['ou=' + part for part in path]

                values = self._getpath(Grimoire.Types.TreeRoot,
                                       path=['directory', 'get', 'ldap'] + revDnList)
                
                gidNumber = values(['gidNumber'])[0]
                
                root = Grimoire.Types.defaultLocalRoot
                clientHomedirPath = values(['cn=defaults', 'grimoireClientHomedirPath'], 'home.people', False)[0].split('.')
                homedirPath = values(['cn=defaults', 'grimoireHomedirPath'])[0].split('.')

                homeDirectory = Grimoire.Utils.encode(root + clientHomedirPath + path + ['group.contents'], 'ascii')

                self._getpath(Grimoire.Types.MethodBase, 2,
                              ['enable', 'directory', 'homedir', 'group'] + homedirPath + path
                              )(group = unicode(Grimoire.Types.UNIXGroup(['groups'] + path)),
                                gid = int(gidNumber),
                                HOME=homeDirectory)
                
                return A(None, "Home directory enabled for group")
            return self._callWithUnlockedTree(unlocked, path)
        
        __dir_allowall__ = False                     
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 2,
                                      ['list', 'ldapentries', '$ldapservername', 'Groups'] + path
                                      )(depth, 'ou=*', addType='ou'))
        
        def _params(self, path):
            return A(Ps([]),
                     Grimoire.Types.Formattable("Enable a home-directory for the group %(group)s",
                                                group=Grimoire.Types.UNIXGroup(['groups'] + path)))
