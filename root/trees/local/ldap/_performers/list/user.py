import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, types, ldap, ldap.filter

objectClasses = ('grimoirePerson',
                 'grimoireAccount',
                 'posixAccount',
                 'CourierMailAccount',
                 'sambaSamAccount',)

excludeAttributes = ['defaultdelivery',
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
    class users(Grimoire.Performer.SubMethod):
        __related__group__ = ['group']
        __path__ = ['user', '$ldapservername']
        def _call(self, path, *arg, **kw):
            class Params(Grimoire.Types.getValue(self._params(path))):
                convertType = Grimoire.Types.convertParamsToUTF8
            kws = Params.compileArgs(arg, [], kw).kws
            filter = '(& ' + ' '.join(  ['(objectClass=' + objectClass + ')' for objectClass in objectClasses]
                                        + ["(%s=%s)" % (key, ldap.filter.escape_filter_chars(value)) for key, value in kws.iteritems()]) + ')'
            return self._getpath(Grimoire.Types.MethodBase,
                                 path=['ldapentries', '$ldapservername', 'People'] + path
                                 )(Grimoire.Performer.UnlimitedDepth, filter, None,
                                   convertToDirList=False, stripTypes=True, addType='ou',
                                   convertToLinks=True, linksReferer=self,
                                   linksBase=self._getpath(Grimoire.Types.TreeRoot, path=['introspection', 'object', 'user', '$ldapservername']))
        __dir_allowall__ = False
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase,
                                      path=['ldapentries', '$ldapservername', 'People'] + path
                                      )(depth, 'ou=*', addType='ou'))
        def _params(self, path):
            params = Grimoire.Types.getValue(self._getpath(Grimoire.Types.MethodBase,
                                                           path=['ldapattributes']
                                                           )(objectClasses, [], excludeAttributes, True))
            params = params.addDefaults({'preferredLanguage':
                                         Grimoire.Types.RestrictedType.derive(types.StringType,
                                                                              [Grimoire.Types.AnnotatedValue('C', 'Default C Locale/English')] + 
                                                                              map(lambda (name, value): Grimoire.Types.AnnotatedValue(value, name.title()),
                                                                                  self._callWithUnlockedTree(lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.sysinfo(['languages', 'sorted'])))),
                                         })
            class params(Grimoire.Types.getValue(params)):
                required=0
            return Grimoire.Types.AnnotatedValue(
                params,
                Grimoire.Types.Formattable("Search for users under %(path)s", path=Grimoire.Types.GrimoirePath(path)))
