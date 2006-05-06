import Grimoire.Utils.Password, Grimoire.Performer, Grimoire.Types, Grimoire.Utils, types, ldap, string, copy, os

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive
R = Grimoire.Types.RestrictedType.derive

NES = Grimoire.Types.NonemptyStringType
NEU = Grimoire.Types.NonemptyUnicodeType

userPathonlyParams = None
def getUserPathonlyParams(obj):
    global userPathonlyParams
    if not userPathonlyParams:
        requiredParameters = [('userPassword',
                               A(Grimoire.Types.NewPasswordType,
                                 'Password/passphrase')),

                              ('sn', A(NEU, 'Surname')),
                              ('givenName', A(NEU, 'Given name')),
                              ]

        optionalParameters = [('initials', A(NEU, 'Initials')),
                              ('grimoireSwedishIDNumber', A(NES, 'Personal identification number')),

                              ('title', A(NEU, 'Title')),
                              ('ou', A(NEU, 'Organizational unit')),
                              ('roomNumber', A(types.IntType, 'Room number')),

                              ('telephoneNumber', A(NES, 'Telephone number')),
                              ('facsimileTelephoneNumber', A(NES, 'Facsimile telephone number')),
                              ('street', A(NEU, 'Street')),
                              ('postOfficeBox', A(NEU, 'Post office box')),
                              ('postalCode', A(NES, 'Postal code')),
                              ('postalAddress', A(NEU, 'Postal address')),

                              ('homePhone', A(NES, 'Home telephone number')),
                              ('homePostalAddress', A(NEU, 'Home postal address')),
                              ('mobile', A(NES, 'Mobile telephone number')),
                              ('pager', A(NES, 'Pager number')),

                              ('preferredLanguage', A(R(types.StringType,
                                                        [A('C', 'Default C Locale/English')] + \
                                                        map(lambda (name, value): A(value, name.title()),
                                                            obj.directory.get.sysinfo(['languages', 'sorted']))),
                                                      'Preferred language')),

                              ('grimoireSecondaryUid', A(NES, 'Mail username')),

                              ('description', A(NEU, 'Description')),
                              ]
        userPathonlyParams = Grimoire.Types.ParamsType.derive(requiredParameters + optionalParameters, len(requiredParameters), None, None)
    return userPathonlyParams

userPathonlyConvertingParams = None
def getDefaultsConvertingParams(obj):
    global userPathonlyConvertingParams
    if not userPathonlyConvertingParams:
        class ParamsType(getUserPathonlyParams(obj)):
            convertType = Grimoire.Types.convertParamsToUTF8
        userPathonlyConvertingParams = ParamsType
    return userPathonlyConvertingParams

userParams = None
def getUserParams(obj):
    global userParams
    if not userParams:
        userPathonlyParams = getUserPathonlyParams(obj)
        class ParamsType(userPathonlyParams):
            arglist = [('uid', A(Grimoire.Types.UsernameType,
                                 'Username (name of user account)'))] + userPathonlyParams.arglist
            required = userPathonlyParams.required + 1
        userParams = ParamsType
    return userParams

convertTypes = Grimoire.Types.ParamsType.derive(resargstype = Grimoire.Types.UTF8Type,
                                                                reskwtype = Grimoire.Types.UTF8Type)

class Performer(Grimoire.Performer.Base):
    class userPathonly(Grimoire.Performer.SubMethod):
        __path__ = ['userPathonly', '$ldapservername']
        def _call(self, path, *args, **kws):
            def unlocked(path, *args, **kws):
                conn = self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(['local', 'ldap', 'admin', 'conn'], cache=True)
                kws = getDefaultsConvertingParams(self._getpath(Grimoire.Types.TreeRoot)).compileArgs(args, [], kws).kws
                path = [Grimoire.Utils.encode(item, 'ascii') for item in path]
                groupPath = path[:-1]
                user = path[-1]

                # Check if the account name is allready taken
                id = conn.search(conn.realm, ldap.SCOPE_SUBTREE,
                                 '(& (! (objectClass=DraftAccount)) (uid=%s))' % Grimoire.Utils.encode(user, 'ascii'),
                                 attrlist=['dn'])
                if len(conn.result(id)[1]) != 0:
                    raise Exception('The proposed username is already taken by someone else in the system. Please choose another one.')
                
                kws['uid'] = user
                kws['cn'] = kws['givenName'] + ' ' + kws['sn']

                revGroupDnList = ['ou=People'] + ['ou=' + part for part in groupPath]
                groupDnList = [item for item in revGroupDnList]
                groupDnList.reverse()
                dnList = ['uid=' + kws['uid']] + groupDnList
                dn = string.join(dnList + [conn.realm], ',')
                
                values = self._getpath(Grimoire.Types.TreeRoot, path=['directory', 'get', 'ldap'] + revGroupDnList)
                
                kws['objectClass'] =  ('grimoirePerson',
                                       'grimoireAccount',
                                       'posixAccount',
                                       'CourierMailAccount',
                                       'sambaSamAccount',)
                kws['owner'] = self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(['local', 'ldap', 'user', 'dn'])
                
                # What the fuck is the interpretation/format of these?
                # Samba needs at least acctFlags to be like this, and the
                # other ones should possibly be set to the current date
                # and the current date plus say one year or whatever,
                # respectively... Hm, are they perheaps days from epoch in
                # hex? Seconds from epoch? Seconds from Windows' epoch?
                kws['sambaPwdLastSet'] = '1075893534'
                kws['sambaPwdMustChange'] = '2147483647'
                kws['sambaAcctFlags'] = '[U          ]'
                
                #### fixme ####
                # description = """Shouldn't we redo the
                # create.user/accept.user so that defaults are read
                # from draft-accounts under cn=defaults?"""
                #### end ####
                kws['loginShell'] = '/bin/bash'
                
                root = Grimoire.Types.defaultLocalRoot
                clientHomedirPath = values(['cn=defaults', 'grimoireClientHomedirPath'], 'home.people', False)[0].split('.')
                clientMaildirPath = values(['cn=defaults', 'grimoireClientMaildirPath'], 'home.mail', False)[0].split('.')
                kws['homeDirectory'] = Grimoire.Utils.encode(root + clientHomedirPath + groupPath + ['group.users', user], 'ascii')
                kws['mailbox'] = Grimoire.Utils.encode(root + clientMaildirPath + groupPath + ['group.users', user], 'ascii') + os.sep
                
                kws['mail'] = kws['uid'] + '@' + values(['cn=defaults', 'grimoireMailDomain'])[0]
                if 'grimoireSecondaryUid' in kws:
                    mailname = kws['grimoireSecondaryUid']
                    del kws['grimoireSecondaryUid']
                    kws['mail'] = (kws['mail'], mailname + '@' + values(['cn=defaults', 'grimoireSecondaryMailDomain'])[0])
                if 'userPassword' in kws:
                    kws['sambaLMPassword'], kws['sambaNTPassword'] = getattr(self._getpath(Grimoire.Types.MethodBase).ntpassword, '$ldapservername')(kws['userPassword'])
                    kws['userPassword'] = "{SSHA}" + Grimoire.Utils.Password.sshaencrypt(kws['userPassword'])
                search = string.join(groupDnList + [conn.realm], ',')
                id = conn.search(string.join(groupDnList + [conn.realm], ','),
                                 ldap.SCOPE_BASE, attrlist=['gidNumber', 'sambaSID'])
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

                homedirPath = values(['cn=defaults', 'grimoireHomedirPath'])[0].split('.')
                maildirPath = values(['cn=defaults', 'grimoireMaildirPath'])[0].split('.')
                conn.add_s(dn, kws.items())

                # Create a home directory
                self._getpath(Grimoire.Types.MethodBase,
                              path=['homedir', 'user'] + homedirPath + groupPath
                              )(user,
                                homeGroup = unicode(Grimoire.Types.UNIXGroup(['people'] + groupPath)),
                                uid = int(kws['uidNumber']),
                                gid = int(kws['gidNumber']),
                                USER=user,
                                HOME=kws['homeDirectory'],
                                MAIL=kws['mailbox'])

                # Get an owner account for the mail files
                maildirowner = self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                    ['local', 'ldap', 'create', 'maildir', 'ownerAccount'],
                    None, 0)

                # Get uid/gid on mailserver for that account, or
                # uid/gid of created user if no account was specified
                mdo_uid = int(kws['uidNumber'])
                mdo_gid = int(kws['gidNumber'])
                if maildirowner:
                    (mdo_name, mdo_passwd, mdo_uid, mdo_gid, mdo_gecos, mdo_dir, mdo_shell) = \
                               self._getpath(Grimoire.Types.TreeRoot,
                                             path=['directory', 'get', 'userinfo'] + maildirPath
                                             )([maildirowner])
                # Create directory, owned by said uid/gid
                self._getpath(Grimoire.Types.MethodBase,
                              path=['maildir', 'user'] + maildirPath + groupPath
                              )(user, mdo_uid, mdo_gid)

                return A(None,
                         'Successfully added user account')
            return self._callWithUnlockedTree(unlocked, path, *args, **kws)
        def _dir(self, path, depth):
            return []
        def _params(self, path):
            return A(self._callWithUnlockedTree(
                         getUserPathonlyParams,
                         self._getpath(Grimoire.Types.TreeRoot)),
                     Grimoire.Types.Formattable(
                         'Create a new user account %(path)s',
                         path=Grimoire.Types.GrimoirePath(path)))

    class user(Grimoire.Performer.SubMethod):
        __path__ = ['user', '$ldapservername']
        __related_group__ = ['home group']
        def _call(self, path, uid, *args, **kws):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase,
                                      path=['userPathonly', '$ldapservername'] + path + [unicode(uid)]
                                      )(*args, **kws))
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 1,
                                      ['list', 'ldapentries', '$ldapservername', 'People'] + path
                                      )(depth, 'ou=*', addType='ou'))
        def _params(self, path):
            return A(self._callWithUnlockedTree(getUserParams, self._getpath(Grimoire.Types.TreeRoot)),
                     Grimoire.Types.Formattable(
                         'Create a new user account under %(path)s',
                         path=Grimoire.Types.GrimoirePath(path)))
