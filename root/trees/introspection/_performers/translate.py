import Grimoire.Performer, Grimoire.Utils, Grimoire.Types, types


Ps = Grimoire.Types.ParamsType.derive
A = Grimoire.Types.AnnotatedValue

class Performer(Grimoire.Performer.Base):
    class translate(Grimoire.Performer.SubMethod):
        def _call(self, path, language, message):
            try:
                return self._physicalGetpath(Grimoire.Types.TreeRoot)._treeOp(path, 'translate', language=language, message=message)
            except AttributeError:
                raise Grimoire.Utils.UntranslatableError('No translation found')
        def _dir(self, path, depth):
            return [(1, [])]
        def _params(self, path):
            return A(Ps([('language', A(types.StringType, 'Language to translate to')),
                         ('message', A(types.StringType, 'String to translate')),
                         ]),
                     'Translates a string from the native language of a method to any available language')
