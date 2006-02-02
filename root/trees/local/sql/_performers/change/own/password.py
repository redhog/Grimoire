import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, types

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class password(Grimoire.Performer.Method):
        def _call(self, newpwd):
            uid = self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                ['local', 'sql', 'user', 'id']))                
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 1,
                                      ['$sqlentry', '$sqlservername', 'users']
                                      )(uid, password=newpwd))
        def _params(self):
            return Grimoire.Types.AnnotatedValue(
                Ps([('newpwd', A(Grimoire.Types.LoseNewPasswordType, 'New password to set'))]),
                'Change your own password')
