import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, types

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive
R = Grimoire.Types.RestrictedType.derive

def getTableParams(tree, table, rows):
    def excludeSerials(param):
        if Grimoire.Utils.isSubclass(Grimoire.Types.getValue(param[1]), Grimoire.Types.SerialType):
            raise Grimoire.Utils.FilterOutError()
        return param
    row = [('id', A(R(types.IntType, rows.list), 'The item to update'))]
    res = Ps(row + Grimoire.Utils.Map(
        excludeSerials,
        Grimoire.Utils.getpath(tree.list.columntype,
                               ['$sqlservername', table])([])), 0)
    return res


class Performer(Grimoire.Performer.Base):
    class info(Grimoire.Performer.Method):
        def _call(self, *args, **kws):
            uid = self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                ['local', 'sql', 'user', 'id']))                
            def unlocked():
                return self._getpath(Grimoire.Types.MethodBase, 2,
                                     ['list', 'nonpath', '$sqlentries', '$sqlservername']
                                     )(['users'])
            rows = Grimoire.Types.getValue(self._callWithUnlockedTree(unlocked))
            params = self._callWithUnlockedTree(getTableParams, self._getpath(Grimoire.Types.MethodBase, 2), 'users', rows)
            class newparams(params):
                arglist = filter(lambda e: e[0] not in ['password', 'usergroup', 'username'], params.arglist) # lose some not-changeable values
            kws = newparams.compileArgs((uid,) + args, [], kws).kws
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 1,
                                      ['$sqlentry', '$sqlservername', 'users']
                                      )(uid, **kws))
        def _params(self):
            def unlocked():
                return self._getpath(Grimoire.Types.MethodBase, 2,
                                     ['list', 'nonpath', '$sqlentries', '$sqlservername']
                                     )([])
            rows = Grimoire.Types.getValue(self._callWithUnlockedTree(unlocked))
            params = self._callWithUnlockedTree(getTableParams, self._getpath(Grimoire.Types.MethodBase, 2), 'users' , rows)
            class newparams(params):
                arglist = filter(lambda e: e[0] not in ['id', 'password', 'usergroup', 'username'], params.arglist) # lose some not-changeable values
            return Grimoire.Types.AnnotatedValue(
                newparams,
                'Change your own info')
