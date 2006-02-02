import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, string, ldap

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

def path2attributeAndDNList(path):
    dnList, keypath = Grimoire.Utils.splitList(path, Grimoire.Types.pathSeparator, 2)
    dnList = dnList + keypath[:-1]
    attribute = keypath[-1]
    return (dnList, attribute)

def path2attributeAndDN(realm, path):
    dnList, attribute = path2attributeAndDNList(path)
    return (Grimoire.Types.DN(Grimoire.Utils.Reverse(realm.split(',')) + dnList),
            attribute)

def path2attributeAndDNMap(realm, path):
    dn, attribute = path2attributeAndDN(realm, path)
    return {'dn': dn,
            'attribute': attribute}

class LdapSubMethod(Grimoire.Performer.SubMethod):
    __dir_allowall__ = False
    def _dir(self, path, depth):
        # FIXME: Not quite implemented yet, huh?
        return [[], [(1, [])]][self._hasAttr(path)]

class Performer(Grimoire.Performer.Base):
    class get_ldap(LdapSubMethod):
        def _call(self, path):
            if path:
                conn = self._callWithUnlockedTree(self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters,
                                                  ['local', 'ldap', 'admin', 'conn'], cache=True)
                dn, attribute = path2attributeAndDN(conn.realm, path)
                id = conn.search(Grimoire.Utils.encode(dn, 'ascii'), ldap.SCOPE_BASE, attrlist=[attribute])
                try:
                    return conn.result(id)[1][0][1][attribute]
                except KeyError:
                    pass
                except ldap.NO_SUCH_OBJECT:
                    pass
            raise AttributeError(path)
        def _hasAttr(self, path):
            if (not path or
                Grimoire.Types.pathSeparator not in path or
                path[-1] == Grimoire.Types.pathSeparator or
                '=' in path[-1]):
                return 0
            try:
                self._call(path)
                return 1
            except AttributeError:
                return 0
        def _params(self, path):
            return A(Ps(),
                     Grimoire.Types.Formattable(
                         'Read the attribute value %(attribute)s in %(dn)s',
                         path2attributeAndDNMap(
                             self._callWithUnlockedTree(
                                 self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters,
                                 ['local', 'ldap', 'admin', 'conn'], cache=True).realm,
                             path)))

    class set_ldap(LdapSubMethod):
        def _call(self, path, value):
            raise NotImplemented
        def _params(self, path):
            return A(Ps([('value', A(Grimoire.Types.AnyType,
                                     'Value to set'))]),
                     Grimoire.Types.Formattable('Sets the attribute %(attribute)s in %(dn)s',
                                               path2attributeAndDNMap(path)))

    class get_user(Grimoire.Performer.SubMethod):
        def _call(self, path):
            if not path or path[0] != Grimoire.Types.pathSeparator:
                raise AttributeError(path)
            path = path[1:]
            def unlocked():
                userDn = Grimoire.Utils.Reverse(
                    self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(['local', 'ldap', 'user', 'dn']).split(','))
                if path == ['language']:
                    return self._getpath(Grimoire.Types.TreeRoot,
                                         path=['directory', 'get', 'ldap'] + userDn
                                         )(['preferredLanguage'])[0]
                raise AttributeError(path)
            return self._callWithUnlockedTree(unlocked)
        def _params(self, path):
            return A(Ps(),
                     Grimoire.Types.Formattable(
                         'Read the %(attribute)s of the current user',
                         Types.Reducible(path[1:], ' ')))
        def _dir(self, path, depth):
            if not depth:
                if (not path or
                    path[0] != Grimoire.Types.pathSeparator):
                    return []
                try:
                    self._call(path)
                    return [(1, [])]
                except AttributeError:
                    return []
            # FIXME: Not quite implemented yet, huh?
            return []
