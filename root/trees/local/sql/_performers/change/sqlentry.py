import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, string, types, stat, os, pg

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive
R = Grimoire.Types.RestrictedType.derive

NES = Grimoire.Types.NonemptyStringType

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
    class sqlentry(Grimoire.Performer.SubMethod):
        __path__ = ['$sqlentry', '$sqlservername']
        def _call(self, path, rowid, *arg, **kws):
            def unlocked():
                return self._getpath(Grimoire.Types.MethodBase, 1,
                                     ['list', 'nonpath', '$sqlentries', '$sqlservername']
                                     )([path[0]])
            rows = Grimoire.Types.getValue(self._callWithUnlockedTree(unlocked))
            kws = self._callWithUnlockedTree(getTableParams, self._getpath(Grimoire.Types.MethodBase, 1), path[0], rows).compileArgs((rowid,) + arg, [], kws).kws
            if not kws:
                return Grimoire.Types.AnnotatedValue("No values to update", None)
            if len(path) != 1: raise AttributeError(path)
            # Get the database object
            db = self._callWithUnlockedTree(lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(['local', 'sql', 'db']))
            db.query("""update %s set %s where "id" = '%s'""" %
            	     (path[0], ', '.join([""""%s" = '%s'""" % item for item in kws.iteritems()]), rowid))
            res = self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 1,
                                      ['list', 'nonpath', '$sqlentries', '$sqlservername']
                                      )(tables = [path[0]], where = """"id" = '%s'""" % rowid))
            return Grimoire.Types.AnnotatedValue(res, "Updated row")

        __dir_allowall__ = False # change.sqlentry can't be called in itself
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 1,
                                      ['list', 'sqltables', '$sqlservername'] + path
                                      )([], depth, isMethodList=[1, 0], listViews=False))
        def _params(self, path):
            def unlocked():
                return self._getpath(Grimoire.Types.MethodBase, 1,
                                     ['list', 'nonpath', '$sqlentries', '$sqlservername']
                                     )([path[0]])
            rows = Grimoire.Types.getValue(self._callWithUnlockedTree(unlocked))
            return A(self._callWithUnlockedTree(getTableParams, self._getpath(Grimoire.Types.MethodBase, 1), path[0], rows),
                     Grimoire.Types.Formattable('Update a row in table %(table)s', table = path[0]))
        
