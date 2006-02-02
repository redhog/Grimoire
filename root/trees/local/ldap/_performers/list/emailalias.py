import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, types, ldap, string

class Performer(Grimoire.Performer.Base):
    class emailalias(Grimoire.Performer.SubMethod):
        __path__ = ['emailalias', '$ldapservername']
        def _call(self, path):
            return None
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase,
                                      path=['ldapentries', '$ldapservername', 'Domains'] + path
                                      )(depth, 'objectClass=CourierMailAlias', addType='ou'))
        def _params(self, path):
            return Grimoire.Types.ParamsType.derive()
