import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, types, ldap, string

class Performer(Grimoire.Performer.Base):
    _hide = Grimoire.Performer.Base._hide + [['emailaliasPathonly', '$ldapservername']]
    
    class emailaliasPathonly(Grimoire.Performer.SubMethod):
        __path__ = ['emailaliasPathonly', '$ldapservername']
        def _call(self, path, maildrop):
            path = Grimoire.Utils.Reverse(path)
            conn = self._callWithUnlockedTree(self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters,
                                              ['local', 'ldap', 'admin', 'conn'], cache=True)
            mailalias = path[0] + '@' + string.join(path[1:], '.')
            dn = string.join(['mail=' + mailalias] + \
                             ['dc=' + part for part in path[1:]] + \
                             ['ou=Domains', conn.realm],
                             ',')
            conn.add_s(dn,
                       [('objectClass', ('organizationalRole', 'CourierMailAlias')),
                        ('cn', Grimoire.Utils.encode(mailalias, 'ascii')),
                        ('mail', Grimoire.Utils.encode(mailalias, 'ascii')),
                        ('maildrop', Grimoire.Utils.encode(maildrop, 'ascii'))])
            return Grimoire.Types.AnnotatedValue(
                None,
                'Mail alias successfully added')
            
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 1,
                                      ['list', 'ldapentries', '$ldapservername', 'Domains'] + path
                                      )(depth, 'objectClass=dcObject', beginType='ou', addType='dc'))
        def _params(self, path):
            return Grimoire.Types.AnnotatedValue(
                Grimoire.Types.ParamsType.derive(
                    [('maildrop',
                      Grimoire.Types.AnnotatedValue(
                          types.StringType,
                          "(Existing) adress to forward mail to")),
                     ]),
                Grimoire.Types.Formattable(
                    'Create a new e-mail-alias %(address)s forwarding its mail to an existing adress',
                    address=Grimoire.Types.EMailAddress(
                        path[-1],
                        Grimoire.Types.DNSDomain(path[:-1]))))

    class emailalias(Grimoire.Performer.SubMethod):
        __path__ = ['emailalias', '$ldapservername']
        def _call(self, path, username, maildrop):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase,
                                      path=['emailaliasPathonly', '$ldapservername'] + path + [username]
                                      )(maildrop))
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 1,
                                      ['list', 'ldapentries', '$ldapservername', 'Domains'] + path
                                      )(depth, 'objectClass=dcObject', beginType='ou', addType='dc'))
        def _params(self, path):
            return Grimoire.Types.AnnotatedValue(
                Grimoire.Types.ParamsType.derive(
                    [('username',
                      Grimoire.Types.AnnotatedValue(
                          types.StringType,
                          'New adress username')),
                     ('maildrop',
                      Grimoire.Types.AnnotatedValue(
                          types.StringType,
                          "(Existing) adress to forward mail to (maildrop)")),
                     ]),
                Grimoire.Types.Formattable(
                    'Create a new e-mail-alias %(address)s forwarding its mail to an existing adress',
                    address=Grimoire.Types.EMailAddress(
                        '(username)',
                        Grimoire.Types.DNSDomain(path))))
