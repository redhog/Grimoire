import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, types, ldap, string

class Performer(Grimoire.Performer.Base):
    _hide = Grimoire.Performer.Base._hide + [['hostPathonly', '$ldapservername']]
    
    class hostPathonly(Grimoire.Performer.SubMethod):
        __path__ = ['hostPathonly', '$ldapservername']
        def _call(self, path, arecord):
            path = Grimoire.Utils.Reverse(path)
            conn = self._callWithUnlockedTree(self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters,
                                              ['local', 'ldap', 'admin', 'conn'], cache=True)
            dn = string.join(['dc=' + part for part in path] + \
                             ['ou=Domains', conn.realm],
                             ',')
            dcname = path[0]
            domain =  string.join(path[1:], '.')
            conn.add_s(dn,[('objectClass', ['dNSZone', 'dcObject']),
                           ('dc', dcname),
                           ('relativeDomainName', dcname),
                           ('aRecord', Grimoire.Utils.encode(arecord, 'ascii')),
                           ('dNSTTL', "3600"),
                           ('zoneName', domain)])
            return Grimoire.Types.AnnotatedValue(
                None,
                'Host successfully added')
        def _dir(self, path, depth):
            return []
        def _params(self, path):
            return Grimoire.Types.AnnotatedValue(
                Grimoire.Types.ParamsType.derive([],
                                                                 0,
                                                                 None,
                                                                 None),
                Grimoire.Types.Formattable(
                    'Create a new host %(domain)s',
                    domain=string.join(Grimoire.Utils.Reverse(path), '.')))

    class host(Grimoire.Performer.SubMethod):
        __path__ = ['host', '$ldapservername']
        def _call(self, path, host, arecord):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase,
                              path=['hostPathonly', '$ldapservername'] + path + Grimoire.Utils.Reverse(host.split('.'))
                              )(arecord))
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 1,
                                      ['list', 'ldapentries', '$ldapservername', 'Domains'] + path)(
                depth, 'objectClass=dcObject', addType='ou'))
        def _params(self, path):
            return Grimoire.Types.AnnotatedValue(
                Grimoire.Types.ParamsType.derive(
                    [('host',
                      Grimoire.Types.AnnotatedValue(
                          types.StringType,
                          "Hostname")),
                     ('arecord',
                      Grimoire.Types.AnnotatedValue(
                          types.StringType,
                          "IP-address to host")),
                     ]),
                Grimoire.Types.Formattable(
                    'Create a new host under %(domain)s',
                    domain=string.join(Grimoire.Utils.Reverse(path), '.')))
