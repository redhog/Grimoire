import Grimoire.Performer, Grimoire.Types



class Performer(Grimoire.Performer.Base):
    class logout(Grimoire.Performer.Method):
        def _call(self):
            def unlocked():
                sess = self._callWithUnlockedTree(
                    lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.treeinfo(['local', 'client', 'logout', 'session']))
                path = self._callWithUnlockedTree(
                    lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.treeinfo(['local', 'client', 'logout', 'path']))
                tree = self._callWithUnlockedTree(
                    lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.treeinfo(['local', 'client', 'logout', 'tree']))
                sess.remove(path, tree)
                return Grimoire.Types.AnnotatedValue(
                    None,
                    'You have been logged out. Good bye!')
            return self._callWithUnlockedTree(unlocked)
        def _params(self):
            path = self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.treeinfo(['local', 'client', 'logout', 'path']))
            return Grimoire.Types.AnnotatedValue(
                Grimoire.Types.ParamsType.derive(),
                Grimoire.Types.Formattable(
                    'Really log out from %(path)s?',
                    path=Grimoire.Types.GrimoirePath(path)))
