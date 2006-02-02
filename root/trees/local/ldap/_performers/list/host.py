import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, types, ldap, string

class Performer(Grimoire.Performer.Base):
    class host(Grimoire.Performer.SubMethod):
        __path__ = ['host', '$ldapservername']
        def _call(self, path):
            return None
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase,
                                      path=['ldapentries', '$ldapservername', 'Domains'] + path
                                      )(depth, '(& (objectClass=dnsZone) (! (soarecord=*)))', addType='ou'))
        def _params(self, path):
            return Grimoire.Types.ParamsType.derive()
