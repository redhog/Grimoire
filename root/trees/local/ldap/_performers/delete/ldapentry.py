import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, types, ldap, string

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class ldapentry(Grimoire.Performer.SubMethod):
        __path__ = ['ldapentry', '$ldapservername']
        def _call(self, path, doDelete = 1):
            conn = self._callWithUnlockedTree(
                lambda : self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                    ['local', 'ldap', 'admin', 'conn'], cache=True))
            dns = [path + pth for (leaf, pth) in
                   self._callWithUnlockedTree(
                       lambda: self._getpath(Grimoire.Types.MethodBase, 1, ['list', 'ldapentries', '$ldapservername'] + path
                                             )(Grimoire.Performer.UnlimitedDepth,
                                               stripTypes = 0))]
            if dns:
                dns.sort(lambda x, y: cmp(len(y), len(x)))
                for dn in dns:
                    conn.delete_s(string.join(Grimoire.Utils.Reverse(dn) + [conn.realm], ','))
                return A(None,
                         'Successfully removed entry')
            else:
                return A(None,
                         'No such entry')
        __dir_allowall__ = False
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 1,
                                      ['list', 'ldapentries', '$ldapservername'] + path
                                      )(depth, stripTypes = 0))
        def _params(self, path):
            return A(Ps(),
                     Grimoire.Types.Formattable(
                         'Delete the ldap entry %(path)s',
                         path=Grimoire.Types.DN(path)))
