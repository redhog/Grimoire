import Grimoire.Utils, Grimoire.Utils.Password, Grimoire.Performer, Grimoire.Types, os

# A list of files to delete from the user's home directory.
# Should probably be taken from LDAP instead, or from a skeleton file. 

gnomeFilesToDelete = [ '.sversionrc',
                       '.gconf',
                       '.gnome2*',
                       '.openoffice' ] 

class Performer(Grimoire.Performer.Base):
    class account_desktop(Grimoire.Performer.SubMethod):
        __path__ = ['account', 'desktop', '$ldapservername']
        __related_group__ = ['user']
        def _call(self, path):
            def unlocked():
                # Fixme: Shouldn't we handle escape-sequences here in some way?
                homedirPath = self._getpath(Grimoire.Types.TreeRoot,
                                            path=['directory', 'get', 'ldap', 'ou=People'] + ['ou=' + part for part in path[:-1]]
                                            )(['cn=defaults', 'grimoireHomedirPath'])[0].split('.')

                user = path[-1]
                groupPath = path[:-1]

                error = []
                for file in gnomeFilesToDelete:
                    try:
                        self._getpath(Grimoire.Types.MethodBase, 1,
                                      [ 'delete', 'file' ] + homedirPath + groupPath + ['group.users', user, file]
                                      )()
                    except Exception, e:
                        error.append(e)
                return Grimoire.Types.AnnotatedValue(error or None, "Reset the users GNOME desktop")
            return self._callWithUnlockedTree(unlocked)

        __dir_allowall__ = False
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 1,
                                      ['list', 'ldapentries', '$ldapservername', 'People'] + path
                                      )(depth, filter = 'uid=*', addType = 'ou', endType = 'uid'))
        
        def _params(self, path):
            return Grimoire.Types.AnnotatedValue(
                Grimoire.Types.ParamsType.derive([], 0),
                Grimoire.Types.Formattable("Reset the GNOME desktop for the user %(user)s",
                                           user=path[-1]))

    class account_shared(Grimoire.Performer.SubMethod):
        __path__ = ['account', 'shared', '$ldapservername']
        __related_group__ = ['user']
        def _call(self, path):
            def unlocked():
                # Fixme: Shouldn't we handle escape-sequences here in some way?
                homedirPath = self._getpath(Grimoire.Types.TreeRoot,
                                            path=['directory', 'get', 'ldap', 'ou=People'] + ['ou=' + part for part in path[:-1]]
                                            )(['cn=defaults', 'grimoireHomedirPath'])[0].split('.')
                clientHomedirPath = self._getpath(Grimoire.Types.TreeRoot,
                                            path=['directory', 'get', 'ldap', 'ou=People'] + ['ou=' + part for part in path[:-1]]
                                                  )(['cn=defaults', 'grimoireClientHomedirPath'])[0].split('.')


                user = path[-1]
                homeGroupPath = path[:-1]

                try:
                    self._getpath(Grimoire.Types.MethodBase, 1,
                                  [ 'delete', 'file' ] + homedirPath + homeGroupPath + ['group.users', user, 'shared']
                                  )()
                except:
                    # Don't care if there is or isn't any shared
                    # directory there yet. Just make sure there's none
                    # after this...
                    pass

                self._getpath(Grimoire.Types.MethodBase, 1,
                              ['create', 'directory'] + homedirPath + homeGroupPath + ['group.users', user]
                              )('shared', uid=0, gid=0)
                self._getpath(Grimoire.Types.MethodBase, 1,
                              ['create', 'symlink'] + homedirPath + homeGroupPath + ['group.users', user, 'shared']
                              )(unicode(Grimoire.Types.UNIXGroup(['people'] + homeGroupPath)), clientHomedirPath + homeGroupPath + ['group.contents'], uid=0, gid=0)

                for groupPath in self._getpath(Grimoire.Types.MethodBase, 1,
                                               ['list', 'user', 'memberships'] + path)():                    
                    clientGroupPath = self._getpath(Grimoire.Types.TreeRoot,
                                                    path=['directory', 'get', 'ldap'] + list(Grimoire.Types.DN(['ou=Groups'] + ['ou=' + item for item in path])),
                                                    )(['cn=defaults', 'grimoireClientHomedirPath'])[0].split('.')
                    self._getpath(Grimoire.Types.MethodBase, 1,
                                  ['create', 'symlink'] + homedirPath + homeGroupPath + ['group.users', user, 'shared']
                                  )(unicode(Grimoire.Types.UNIXGroup(['groups'] + groupPath)),
                                    clientGroupPath + groupPath + ['group.contents'],
                                    uid=0, gid=0)

                return Grimoire.Types.AnnotatedValue(None, "Reset the user's shared directory")
            return self._callWithUnlockedTree(unlocked)

        __dir_allowall__ = False
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 1,
                                      ['list', 'ldapentries', '$ldapservername', 'People'] + path
                                      )(depth, filter = 'uid=*', addType = 'ou', endType = 'uid'))
        
        def _params(self, path):
            return Grimoire.Types.AnnotatedValue(
                Grimoire.Types.ParamsType.derive([], 0),
                Grimoire.Types.Formattable("Reset the shared-directory for the user %(user)s",
                                           user=path[-1]))
