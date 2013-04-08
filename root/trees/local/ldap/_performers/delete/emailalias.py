import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, types, ldap, string

class Performer(Grimoire.Performer.Base):
    class emailalias(Grimoire.Performer.SubMethod):
        __path__ = ['emailalias', '$ldapservername']
        def _call(self, path):
            domain = string.join(Grimoire.Utils.Reverse(path[:-1]), ".")
            dn = ['ou=Domains'] + [ "dc="+elem for elem in path[0:-1]] + [ "mail="+path[-1]]
            def unlocked():
                return self._getpath(Grimoire.Types.MethodBase, path=['ldapentry', '$ldapservername'] + dn)()
            return self._callWithUnlockedTree(unlocked)
                                       
        __dir_allowall__ = False
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 1,
                                      ['list', 'ldapentries', '$ldapservername', 'Domains'] + path
                                      )(depth, 'objectClass=CourierMailAlias', beginType = 'ou', addType='dc', endType='mail'))

        def _params(self, path):
            return Grimoire.Types.AnnotatedValue(
                Grimoire.Types.ParamsType.derive([]),
                Grimoire.Types.Formattable(
                    'Delete the e-mail-alias %(address)s',
                    address=Grimoire.Types.EMailAddress(
                        path[-1].split('@')[0],
                        Grimoire.Types.DNSDomain(path[0:-1]))))
