import Grimoire.Performer, Grimoire.Types, Grimoire.Types.Ability, Grimoire.Utils, types, ldap, string

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class abstractGroup(Grimoire.Performer.SubMethod):
        __path__ = ['abstract group', '$ldapservername']
        def _call(self, path, name):
            conn = self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(['local', 'ldap', 'admin', 'conn'], cache=True))
            userdn = self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(['local', 'ldap', 'user', 'dn'], cache=True))
            username = userdn.split(',', 1)[0].split('=', 1)[1]

            cn = Grimoire.Utils.encode(Grimoire.Types.UNIXGroup(path + [name]), 'utf-8')
            dn = Grimoire.Utils.encode(Grimoire.Types.DN(conn.realm) + ['ou=' + item for item in path + [name]], 'utf-8')
            
            gidNumber = self._callWithUnlockedTree(
                lambda: getattr(self._getpath(Grimoire.Types.MethodBase).uniqueId, '$ldapservername'
                                )('gidNumber'))
            gid = Grimoire.Utils.encode(gidNumber, 'ascii')

            # Get the samba base SID from LDAP
	    sambaDomainSID = conn.result(conn.search(conn.realm, ldap.SCOPE_SUBTREE, filterstr='objectClass=sambaDomain',
                                                     attrlist=['sambaSID']))[1][0][1]['sambaSID'][0]
            sambaGroupRID = (gidNumber * 2) + 1001
            sambaSID = "%s-%s" %(sambaDomainSID, sambaGroupRID)

            conn.add_s(dn, [('objectClass', ('grimoireGroup', 'posixGroup', 'sambaGroupMapping')),
                            ('owner', userdn),
                            ('memberUid', username),
                            ('ou', name), 
                            ('cn', cn),
                            ('gidNumber', gid),
                            ('sambaGroupType', '2'),
                            ('sambaSID', sambaSID)])

            return A(gidNumber,
                     'Successfully added new group')

        def _dir(self, path, depth):
            return []
        def _params(self, path):
            typePath, groupPath = Grimoire.Utils.splitList(path, Grimoire.Types.pathSeparator, 2)
            return A(Ps(),
                     Grimoire.Types.Formattable(
                         'Create a new group %(groupPath)s of type %(typePath)s',
                         typePath=Grimoire.Types.GrimoirePath(typePath),
                         groupPath=Grimoire.Types.GrimoirePath(groupPath)))

    class group(Grimoire.Performer.SubMethod):
        __path__ = ['group', '$ldapservername']
        __related_group__ = ['group']
        def _call(self, path, name):
            name = unicode(name)
            def unlocked():
                values = self._getpath(Grimoire.Types.TreeRoot,
                                       path=['directory', 'get', 'ldap', 'ou=groups'] + ['ou=' + item for item in path])
                grimoireHomedirPath = values(['cn=defaults', 'grimoireHomedirPath'], 'home.groups', False)[0].split('.')
                grimoireClientHomedirPath = values(['cn=defaults', 'grimoireClientHomedirPath'], 'home.groups', False)[0].split('.')
                maildirPath = values(['cn=defaults', 'grimoireMaildirPath'])[0].split('.')

                res = self._getpath(Grimoire.Types.MethodBase,
                                    path=['abstract group', '$ldapservername', 'groups'] + path
                                    )(name)
                gid = Grimoire.Types.getValue(res)

                self._getpath(Grimoire.Types.MethodBase,
                              path=['homedir', 'group'] + grimoireHomedirPath + path
                              )(name, gid,
                                HOME = unicode(Grimoire.Types.defaultLocalRoot + grimoireClientHomedirPath + path + [name] + ['group.contents']))

                self._getpath(Grimoire.Types.MethodBase,
                              path=['maildir', 'group'] + maildirPath + path
                              )(name, gid)

                def allow(subject, *paths):
                    self._getpath(Grimoire.Types.MethodBase, path=['ability', 'dn', '$ldapservername'] + subject)(
                        Grimoire.Types.Ability.List([(Grimoire.Types.Ability.Allow, path)
                                                     for path in paths]))
                # Grant some abilities to the new owner and to the group
                allow(Grimoire.Utils.Reverse(
                          self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                              ['local', 'ldap', 'user', 'dn']).split(',')),
                      ['change', 'ability', 'allow', 'groups'] + path,
                      ['change', 'ability', 'cancel', 'allow', 'groups'] + path,
                      ['change', 'group', 'add member'] + path,
                      ['change', 'group', 'remove member'] + path,
                      ['create', 'group'] + path,
                      ['delete', 'group'] + path)
                allow(['ou=' + item for item in ['groups'] + path + [name]],
                      ['create', 'group'] + path + [''])
                return res
            return self._callWithUnlockedTree(unlocked)

        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 1,
                                      ['list', 'ldapentries', '$ldapservername', 'Groups'] + path
                                      )(depth, 'ou=*', addType='ou'))
        def _params(self, path):
            return A(Ps([('name', A(Grimoire.Types.UsernameType,
                                   'Name of new group'))]),
                     Grimoire.Types.Formattable(
                         'Create a new group under %(path)s',
                         path=Grimoire.Types.GrimoirePath(path)))


    class homeGroup(Grimoire.Performer.SubMethod):
        __path__ = ['home group', '$ldapservername']
        __related_group__ = ['home group']
        def _call(self, path, name):
            name = unicode(name)
            def unlocked():
                values = self._getpath(Grimoire.Types.TreeRoot,
                                       path=['directory', 'get', 'ldap', 'ou=people'] + ['ou=' + item for item in path])
                grimoireHomedirPath = values(['cn=defaults', 'grimoireHomedirPath'], 'home.groups', False)[0].split('.')
                grimoireClientHomedirPath = values(['cn=defaults', 'grimoireClientHomedirPath'], 'home.groups', False)[0].split('.')

                res = self._getpath(Grimoire.Types.MethodBase,
                                    path=['abstract group', '$ldapservername', 'people'] + path
                                    )(name)
                gid = Grimoire.Types.getValue(res)

                self._getpath(Grimoire.Types.MethodBase,
                              path=['homedir', 'homegroup'] + grimoireHomedirPath + path
                              )(name, gid,
                                HOME = unicode(Grimoire.Types.defaultLocalRoot + grimoireClientHomedirPath + path + [name] + ['group.contents']))

                self._getpath(Grimoire.Types.MethodBase,
                              path=['maildir', 'homegroup'] + grimoireHomedirPath + path
                              )(name, gid)

                return res
            return self._callWithUnlockedTree(unlocked)

        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 1,
                                      ['list', 'ldapentries', '$ldapservername', 'Groups'] + path
                                      )(depth, 'ou=*', addType='ou'))
        def _params(self, path):
            return A(Ps([('name', A(Grimoire.Types.UsernameType,
                                   'Name of new group'))]),
                     Grimoire.Types.Formattable(
                         'Create a new home group under %(path)s',
                         path=Grimoire.Types.GrimoirePath(path)))
