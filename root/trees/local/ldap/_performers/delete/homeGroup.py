import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, types, ldap, string

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class homeGroup(Grimoire.Performer.SubMethod):
        __path__ = ['homeGroup', '$ldapservername']
        __related_group__ = ['home group']
        def _call(self, path):
            return A(
                Grimoire.Types.getValue(
                    self._callWithUnlockedTree(
                        lambda: self._getpath(Grimoire.Types.MethodBase,
                                              path=['ldapentry', '$ldapservername', 'ou=People'] + ['ou=' + x for x in path]
                                              )())),
                'Successfully deleted the group')
        __dir_allowall__ = False
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 1,
                                      ['list', 'ldapentries', '$ldapservername', 'People'] + path
                                      )(depth, 'objectClass=grimoireGroup', addType='ou'))
        def _params(self, path):
            return A(Ps(),
                     Grimoire.Types.Formattable(
                         'Delete the homegroup %(path)s',
                         path=path))
