import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, types, ldap, string

class Performer(Grimoire.Performer.Base):
    _hide = Grimoire.Performer.Base._hide + [['domainPathonly', '$ldapservername']]
    
    class domainPathonly(Grimoire.Performer.SubMethod):
        __path__ = ['domainPathonly', '$ldapservername']
        def _call(self, path):
            conn = self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                    ['local', 'ldap', 'admin', 'conn'], cache=True))
            dn = ','.join(['dc=' + x for x in Grimoire.Utils.Reverse(path)] + ['ou=Domains', conn.realm])
            try:
                conn.add_s(dn, [('objectClass', ['organizationalUnit', 'dcObject']),
                                ('ou', path[-1]),
                                ('dc', path[-1])])
            except ldap.NO_SUCH_OBJECT, e:
                prepathlen = len(e[0]['matched'].split(',')) - len(conn.realm.split(',')) - 1
                createpath = path[:prepathlen]
                for name in path[prepathlen:]:
                    createpath.append(name)
                    self._getpath(path=createpath)()
            return Grimoire.Types.AnnotatedValue(
                None,
                'Domain successfully added')
        def _dir(self, path, depth):
            return []
        def _params(self, path):
            return Grimoire.Types.AnnotatedValue(
                Grimoire.Types.ParamsType.derive(),
                Grimoire.Types.Formattable(
                    'Create a new domain %(domain)s',
                    domain=Grimoire.Types.DNSDomain(path)))

    class domain(Grimoire.Performer.SubMethod):
        __path__ = ['domain', '$ldapservername']
        def _call(self, path, domain):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase,
                                      path=['domainPathonly'] + path + Grimoire.Utils.Reverse(domain.split('.')))())
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 1,
                                      ['list', 'ldapentries'] + ['$ldapservername', 'ou=Domains'] + ['dc=' + item for item in path]
                                      )(depth, 'objectClass=dcObject') +
                [(1, [])])
        
        def _params(self, path):
            return Grimoire.Types.AnnotatedValue(
                Grimoire.Types.ParamsType.derive(
                    [('domain',
                      Grimoire.Types.AnnotatedValue(
                          types.StringType,
                          "Domainname of domain to create")),
                     ]),
                Grimoire.Types.Formattable(
                    'Create a new domain under %(domain)s',
                    domain=Grimoire.Types.DNSDomain(path)))
