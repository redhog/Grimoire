import Grimoire.Performer, Grimoire.Types, Grimoire.Utils

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class ParametersSubMethod(Grimoire.Performer.SubMethod):
    def _dir(self, path, depth):
        if not depth:
            if tuple(path) in self._physicalBase()._data:
                return [(1, [])]
            return []
        return Grimoire.Performer.DirListFilter(
            path, depth, 
            Grimoire.Utils.Map(lambda path: (1, list(path)),
                               self._physicalBase()._data.iterkeys()))

def path2keypathAndPathStrings(path):
    return {'keypath':
            Grimoire.Types.Reducible(
                Grimoire.Utils.splitList(path,
                                         Grimoire.Types.pathSeparator, 2)[1],
                '.'),
            'path':
            Grimoire.Types.Reducible(
                Grimoire.Utils.splitList(path,
                                         Grimoire.Types.pathSeparator, 2)[0],
                '.'),
            }

class Performer(Grimoire.Performer.Base):
    def __init__(self, data = None):
        Grimoire.Performer.Base.__init__(self)
        self._data = data or {}

    class get(ParametersSubMethod):
        __dir_allowall__ = False
        def _call(self, path):
            try:
                return self._physicalBase()._data[tuple(path)]
            except KeyError:
                raise AttributeError(path)
        def _params(self, path):
            return A(Ps(),
                     Grimoire.Types.Formattable('Read the configuration value %(keypath)s in %(path)s',
                                               **path2keypathAndPathStrings(path)))

    class set(ParametersSubMethod):
        def _call(self, path, value):
            self._physicalBase()._data[tuple(path)] = value
            return A(None, 'Done')
        def _params(self, path):
            return A(Ps([('value', A(Grimoire.Types.AnyType,
                                     'Value to set'))]),
                     Grimoire.Types.Formattable('Sets configuration value %(keypath)s in %(path)s',
                                                **path2keypathAndPathStrings(path)))

    class new_data(Grimoire.Performer.Method):
        def _call(self, data = {}):
            parent = None
            return self._physicalBase().__class__(data)
        def _params(self):
            return A(Ps([('data', A(Grimoire.Types.AnyType, 'Mapping (from keypaths as tuples to values) to use for data'))],
                        0),
                     'Create a new data tree')
