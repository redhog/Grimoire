import Grimoire.Performer, Grimoire.Types, Grimoire.Types.Ability, types

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class client(Grimoire.Performer.Method):
        def _call(self):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase).load.standardtree(
                    __name__ + '._performers',
                    ['parameters'],
                    ['local', 'client', 'initcommands'],
                    Grimoire.Types.Ability.List([
                        (Grimoire.Types.Ability.Deny, ['directory']),
                        (Grimoire.Types.Ability.Deny, ['trees']),
                        (Grimoire.Types.Ability.Deny, ['clients']),
                        (Grimoire.Types.Ability.Allow, [])])))
        def _params(self):
            return A(Ps(),
                     'Returns a tree with client convenience/utility functions')
