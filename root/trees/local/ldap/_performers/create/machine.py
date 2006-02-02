import Grimoire.Utils.Password, Grimoire.Performer, Grimoire.Types, Grimoire.Utils, types, ldap, string, copy, os

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive
R = Grimoire.Types.RestrictedType

NES = Grimoire.Types.NonemptyStringType
NEU = Grimoire.Types.NonemptyUnicodeType

requiredParameters = [('machineName', A(NEU, 'Name'))]
optionalParameters = [('description', A(NEU, 'Description'))]

class Performer(Grimoire.Performer.Base):
    class machinePathonly(Grimoire.Performer.SubMethod):
        __path__ = ['machinePathonly', '$ldapservername']
        def _call(self, path, *args, **kws):
            def unlocked(path, machineName, description = u'Generic client computer'):
                machineName = Grimoire.Utils.encode(machineName, 'ascii')
                description = Grimoire.Utils.encode(description, 'ascii')
                
                kws = { 'uid' : machineName + '$',
                        'description' : description,
                        'cn' : machineName }
                conn = self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(['local', 'ldap', 'admin', 'conn'], cache=True)
                userdn = self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(['local', 'ldap', 'user', 'dn'], cache=True)
                path = [Grimoire.Utils.encode(item, 'ascii') for item in path]
                
                id = conn.search(conn.realm, ldap.SCOPE_SUBTREE,
                                 '(& (! (objectClass=grimoireDraftAccount)) (uid=%s))' % Grimoire.Utils.encode(kws['uid'], 'ascii'),
                                 attrlist=['dn'])
                if len(conn.result(id)[1]) != 0:
                    raise Exception('The proposed machine name is already taken. Please choose another one.')
                
                revGroupDnList = ['ou=Machines'] + ['ou=' + part for part in path[:-1]]
                groupDnList = [item for item in revGroupDnList]
                groupDnList.reverse()
                dnList = ['cn=' + machineName] + groupDnList
                dn = string.join(dnList + [conn.realm], ',')

                values = self._getpath(Grimoire.Types.TreeRoot, path=['directory', 'get', 'ldap'] + revGroupDnList)
                
                kws['objectClass'] =  ('grimoireMachine',
                                       'device',
                                       'posixAccount',
                                       'sambaSamAccount')
                kws['owner'] = userdn
                kws['sambaAcctFlags'] = '[W          ]'
                kws['loginShell'] = '/bin/false'
                kws['homeDirectory'] = '/dev/null'
                # Make the password from the machine name
                kws['sambaLMPassword'], kws['sambaNTPassword'] = getattr(self._getpath(Grimoire.Types.MethodBase).ntpassword, '$ldapservername')(machineName)

                # The group for machines in the ldap database.
                # This could be in ldap or configuration
                clientGroupDnList = self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                    ['local', 'ldap', 'create', 'machine', 'clientGroupDn'])
                search = string.join(clientGroupDnList + [conn.realm], ',')
                id = conn.search(search, ldap.SCOPE_BASE, attrlist=['gidNumber', 'sambaSID'])
                res = conn.result(id)
                kws['gidNumber'] = res[1][0][1]['gidNumber'][0]
                kws['SambaPrimaryGroupSID'] = res[1][0][1]['sambaSID'][0]
                
                uidNumber = getattr(self._getpath(Grimoire.Types.MethodBase).uniqueId, '$ldapservername')('uidNumber')
                kws['uidNumber'] = Grimoire.Utils.encode(uidNumber, 'ascii')
                
                # Create a Samba SID: <domain sid>-<user rid>
                # Search for the domain sid in the LDAP database
                sambaSID = conn.result(conn.search(string.join(['cn=sambaDomain', conn.realm], ','),
                                                   ldap.SCOPE_BASE, attrlist=['sambaSID']))[1][0][1]['sambaSID'][0]
                sambaUserRID = (uidNumber * 2) + 1000
                kws['sambaSID'] = "%s-%s" %(sambaSID, sambaUserRID)
                
                conn.add_s(dn, kws.items())
                
                return A(None, 'Successfully added machine.')
            return self._callWithUnlockedTree(unlocked, path, *args, **kws)
        def _dir(self, path, depth):
            return []
        def _params(self, path):
            return A(Grimoire.Types.ParamsType.derive(requiredParameters + optionalParameters, 1), 
                     Grimoire.Types.Formattable(
                         'Create a new machine account %(path)s',
                         path=Grimoire.Types.GrimoirePath(path)))

    class machine(Grimoire.Performer.SubMethod):
        __path__ = ['machine', '$ldapservername']
        def _call(self, path, *args, **kws):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase,
                                      path=['machinePathonly', '$ldapservername'] + path
                                      )(*args, **kws))
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 1,
                                      ['list', 'ldapentries', '$ldapservername', 'Machines'] + path
                                      )(depth, 'ou=*', addType='ou'))
        def _params(self, path):
            return A(Grimoire.Types.ParamsType.derive(requiredParameters + optionalParameters, 1), 
                     Grimoire.Types.Formattable(
                         'Create a new machine account under %(path)s',
                         path=Grimoire.Types.GrimoirePath(path)))
