import Grimoire.Performer, Grimoire.Types

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive


class Performer(Grimoire.Performer.Base):
    class introspection(Grimoire.Performer.Method):
        def _call(self):
            return self._callWithUnlockedTree(lambda: self._getpath(Grimoire.Types.MethodBase).local.load(__name__ + '._performers'))
        def _params(self):
            return A(Ps(),
                     'This class is a Grimoire tree, that when added with a Composer to anothe tree, provides introspective information such as a method liting, function parameter descriptions, etc, about the other tree. The information is gathered using for the purpose builtin properties of the classes of the Performer module')
