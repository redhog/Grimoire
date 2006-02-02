import Grimoire.Performer, Grimoire.Types.Ability, Grimoire.Types, types


Ps = Grimoire.Types.ParamsType.derive
A = Grimoire.Types.AnnotatedValue

class Performer(Grimoire.Performer.Base):
    class mount(Grimoire.Performer.Method):
        def _call(self, tree, isolate = True):
            if isolate:
                tree = Grimoire.Performer.Isolator(tree)
            self._physicalGetpath(Grimoire.Types.TreeRoot)._insert(tree, False)
            return A(None,
                     'Tree successfully mounted')
        def _params(self):
            return A(Ps([('tree', A(Grimoire.Performer.Performer,
                                    'Tree to mount')),
                         ('isolate', A(types.BooleanType,
                                       "Isolate the mounted tree from the main tree (make it think it's the whole world)"))]),
                     'Mounts a Grimoire tree in the current tree (if supported! _getpath(Grimoire.Types.TreeRoot) must not be a Cutter for this to work)')

    class restrict(Grimoire.Performer.Method):
        def _call(self, tree, ability):
            return Grimoire.Performer.Restrictor(tree, ability)
        def _params(self):
            return A(Ps([('tree', A(Grimoire.Performer.Performer,
                                    'Tree to restrict')),
                         ('ability', A(Grimoire.Types.Ability.List,
                                     'Ability governing access to the resulting tree'))]),
                     'Restricts access to a Grimoire tree')

    class prefix(Grimoire.Performer.Method):
        def _call(self, prefix, tree):
            return Grimoire.Performer.Prefixer(prefix, tree)
        def _params(self):
            return A(Ps([('tree', A(Grimoire.Performer.Performer,
                                    'Tree to prefix')),
                         ('prefix', A(Grimoire.Types.UnicodeList,
                                     'Path to prepend'))]),
                     'Prefixes all paths in a Grimoire tree with some path')

    class compose(Grimoire.Performer.Method):
        def _call(self, *trees):
            return Grimoire.Performer.Composer(*trees)
        def _params(self):
            return A(Ps([], 0, A(Grimoire.Performer.Performer,
                                 'Trees to merge')),
                     'Merges a set of Grimoire trees into one')
