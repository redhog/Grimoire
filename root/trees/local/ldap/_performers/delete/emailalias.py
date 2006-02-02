import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, types, ldap, string

class Performer(Grimoire.Performer.Base):
    class emailalias(Grimoire.Performer.SubMethod):
        __path__ = ['emailalias', '$ldapservername']
        def _call(self, path):
            domain = string.join(Grimoire.Utils.Reverse(path[:-1]), ".")
            dn = ['ou=Domains'] + [ "dc="+elem for elem in path[0:-1]] + [ "mail="+path[-1]+"@"+domain]
            def unlocked():
                return self._getpath(Grimoire.Types.MethodBase, path=['ldapentry', '$ldapservername'] + dn)()
            return self._callWithUnlockedTree(unlocked)
                                       
        __dir_allowall__ = False
        def _dir(self, path, depth):
            # We have to add the "dc=" ourselves and not by
            # using addType, since Domains is a different type (ou)
            # than the rest of the path (dc).
            # /Bjornsson
            path = [ 'dc='+elem for elem in path ]
            result = self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 1,
                                      ['list', 'ldapentries', '$ldapservername', 'ou=Domains'] + path
                                      )(-1, 'objectClass=CourierMailAlias'))
            # Strip the domain suffix of the mail address,
            # if present
            realres = []
            for elem in result:
                realres += [(elem[0], map(lambda x: string.split(x, "@")[0], elem[1]))]
            return realres 

        def _params(self, path):
            return Grimoire.Types.AnnotatedValue(
                Grimoire.Types.ParamsType.derive([]),
                Grimoire.Types.Formattable(
                'Delete the e-mail-alias %(address)s',
                address=Grimoire.Types.EMailAddress(
                path[-1],
                Grimoire.Types.DNSDomain(path[0:-1]))))
