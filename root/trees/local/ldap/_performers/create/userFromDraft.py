import Grimoire.Utils.Password, Grimoire.Performer, Grimoire.Types, Grimoire.Utils, types, ldap, string, copy

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):    
    class user_fromDraft(Grimoire.Performer.SubMethod):
        __path__ = ['user', 'fromDraft', '$ldapservername']
        def _call(self, path, accept, *arg, **kw):
            conn = self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                    ['local', 'ldap', 'admin', 'conn'], cache=True))

            revPath = Grimoire.Utils.Reverse(path)
            dn = string.join(['grimoireSwedishIDNumber=' + revPath[0]] +
                             ['ou=' + item for item in revPath[1:]] +
                             ['ou=People', 'ou=Drafts', conn.realm], ',')

            if accept:
                id = conn.search(dn, ldap.SCOPE_BASE, attrlist=['userPassword', 'member'])
                attrs = conn.result(id)[1][0][1]
                userPassword = Grimoire.Types.NewPasswordType(attrs['userPassword'][0])
                res =self._getpath(Grimoire.Types.MethodBase,
                                   path=['user', '$ldapservername'] + path[:-1]
                                   )(arg[0], userPassword, *arg[1:], **kw)
                if 'member' in attrs:
                    for group in attrs['member']:
                        self._getpath(Grimoire.Types.MethodBase, 1,
                                      ['change', 'group', 'addMember', '$ldapservername'] + Grimoire.Utils.Reverse(
                                          [part.split('=')[1]
                                           for part in group[:-len(',ou=Groups,' + conn.realm)].split(',')])
                                      )(arg[0])
                conn.delete_s(dn)
                res = Grimoire.Types.getValue(res)
                return A(res, 'User account successfully accepted')
            else:
                conn.modify_s(dn, [(ldap.MOD_DELETE, 'draftReady', None)])
                return A(None, 'User account denied')
            return None
        __dir_allowall__ = False
        def _dir(self, path, depth):
            # (uid=*) (sn=*) (cn=*) to only get drafts that are ready to be accepted (a real account must have an uid).
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 1,
                                      ['list', 'ldapentries', '$ldapservername', 'ou=Drafts', 'ou=People'] + ['ou=' + part for part in path]
                                      )(depth,
                                        '(& (objectClass=grimoireDraftAccount) (grimoireDraftReady=*) (uid=*) (sn=*) (cn=*) (userPassword=*))'))
        def _params(self, path):
            conn = self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                    ['local', 'ldap', 'admin', 'conn'], cache=True))

            revPath = Grimoire.Utils.Reverse(path)
            dn = string.join(['grimoireSwedishIDNumber=' + revPath[0]] +
                             ['ou=' + item for item in revPath[1:]] +
                             ['ou=People', 'ou=Drafts', conn.realm], ',')
            
            id = conn.search(dn, ldap.SCOPE_BASE)
            attrs = conn.result(id)[1][0][1]

            def addDefaultValue((name, type)):
                if name == 'userPassword':
                    raise Grimoire.Utils.FilterOutError()
                if name in attrs:
                    comment = Grimoire.Types.getComment(type)
                    type = Grimoire.Types.getValue(type)
                    if Grimoire.Utils.isDescendant(type, Grimoire.Types.ValuedType):
                        restricted = Grimoire.Utils.isDescendant(type, Grimoire.Types.RestrictedType)
                        values = []
                        for value in attrs[name]:
                            if not restricted or value in type.values:
                                values += [value]
                        for value in type.values:
                            if value not in values:
                                values += [value]
                        type = copy.copy(type)
                        type.values = values
                    else:
                        type = Grimoire.Types.HintedType.derive(type, attrs[name])
                    if comment is not None:
                        type = A(type, comment)
                return (name, type)

            params = Grimoire.Types.getValue(
                self._callWithUnlockedTree(
                    lambda: self._getpath(Grimoire.Types.TreeRoot,
                                          path=['introspection', 'params'] +
                                          self._physicalGetpath(Grimoire.Types.MethodBase, 0, ['user', '$ldapservername'])._pathForSelf()
                                          )()))
            arglist = list(Grimoire.Utils.Map(addDefaultValue, params.arglist))

            return A(Ps([('accept', A(Grimoire.Types.BooleanType,
                                      'Accept this user account?'))] + arglist,
                        1 + params.required - 1, # -1 for userPassword
                        params.resargstype, params.reskwtype),
                     Grimoire.Types.Formattable(
                         'Accept user account at %(place)s for user with personal identification number %(grimoireSwedishIDNumber)s',
                         place=Grimoire.Types.GrimoirePath(path[:-1]),
                         grimoireSwedishIDNumber=path[-1]))
