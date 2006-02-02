import Grimoire.Utils, Grimoire.Performer, Grimoire.Types, ldap, string

excludeAttributes = ['uid',

                     'defaultdelivery',
                     'sambaProfilePath',
                     'sambaPasswordHistory',
                     'sambaBadPasswordCount',
                     'clearPassword',
                     'sharedgroup',
                     'gn',
                     'sambaLogoffTime',
                     'description',
                     'organizationalUnitName',
                     'sambaHomePath',
                     'sambaMungedDial',
                     'sambaDomainName',
                     'sambaPwdCanChange',
                     'sambaLogonTime',
                     'sambaLogonScript',
                     'sambaUserWorkstations',
                     'postOfficeBox',
                     'sambaBadPasswordTime',
                     'sambaLMPassword',
                     'sambaAcctFlags',
                     'sambaLogonHours',
                     'sambaKickoffTime',
                     'sambaPwdLastSet',
                     'sambaPrimaryGroupSID',
                     'sambaNTPassword',
                     'internationaliSDNNumber',
                     'sambaPwdMustChange',
                     'sambaHomeDrive',
                     'sambaSID',

                     'disableimap',
                     'disablepop3',
                     'disableshared',
                     'disablewebmail',
                     'quota',

                     'objectClass',
                     'homeDirectory',
                     'gidNumber',
                     'uidNumber',
                     
                     'mailbox',
                     'mail',

                     'userPassword',
                     'pwdLastSet',
                     'acctFlags',
                     'smbHome',
                     'homeDrive',
                     'lmPassword',
                     'ntPassword',
                     'grouprid',
                     'rid',
                     'ntuid',
                     
                     # These might be included, if you really want to confuse the user and/or you have nice widgets for entering them :]
                     
                     'loginShell',
                     'gecos',
                     
                     'pwdCanChange',
                     'pwdMustChange',
                     'logonTime',
                     'logoffTime',
                     'kickoffTime',
                     'workstations',
                     'logonhrs',
                     'script',
                     'profile',
                     
                     'x121Address',
                     'registeredAddress',
                     'destinationIndicator',
                     'preferredDeliveryMethod',
                     'telexNumber',
                     'teletexTerminalIdentifier',
                     'physicalDeliveryOfficeName',
                     'st',
                     'l',
                     
                     'audio',
                     'businessCategory',
                     'carLicense',
                     'departmentNumber',
                     'displayName',
                     'employeeNumber',
                     'employeeType',
                     'jpegPhoto',
                     'labeledURI',
                     'manager',
                     'o',
                     'photo',
                     'secretary',
                     'userCertificate',
                     'x500uniqueIdentifier',
                     'userSMIMECertificate',
                     'userPKCS12',
                     ]

class Performer(Grimoire.Performer.Base):
    class ldapentry(Grimoire.Performer.SubMethod):
        __related__group__ = ['user']
        __path__ = ['user', '$ldapservername']
        def _call(self, path, *args, **kws):
            return self._getpath(Grimoire.Types.MethodBase,
                                 path=['ldapentry', '$ldapservername', 'ou=People'] + ['ou=' + part for part in path[:-1]] + ['uid=' + path[-1]]
                                 )(excludeArgs=excludeAttributes, *args, **kws)
        
        __dir_allowall__ = False #- setting this leads to recursion depth problems
        def _dir(self, path, depth):
           return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 1,
                                      ['list', 'ldapentries', '$ldapservername', 'People'] + path
                                      )(depth, filter = 'uid=*', addType = 'ou', endType = 'uid'))
       
        def _params(self, path):
            return Grimoire.Types.AnnotatedValue(
                Grimoire.Types.getValue(
                    self._callWithUnlockedTree(
                        lambda: self._getpath(Grimoire.Types.TreeRoot,
                                              path=['introspection', 'params'] + self._physicalGetpath(
                                                  Grimoire.Types.MethodBase,
                                                  path=['ldapentry', '$ldapservername', 'ou=People'] + ['ou=' + part for part in path[:-1]] + ['uid=' + path[-1]]
                                                  )._pathForSelf()
                                              )())
                    ).removeArgs(*excludeAttributes),
                Grimoire.Types.Formattable('Change user %(user)s', user=Grimoire.Types.GrimoirePath(path)))
                
            
            
