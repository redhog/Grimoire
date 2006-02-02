import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, string, types, stat, os, pg

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive
R = Grimoire.Types.RestrictedType.derive

class Performer(Grimoire.Performer.Base):
    class sqlentry(Grimoire.Performer.SubMethod):
        __path__ = ['$sqlentry', '$sqlservername']
        def _call(self, path, id):
            if len(path) != 1:
                raise AttributeError()
            sqldeletequery = "delete from "+path[0]+" where id = "+str(id)
            def unlocked():
                return self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(['local', 'sql', 'db'], None)
            dbconn = self._callWithUnlockedTree(unlocked)
            res = dbconn.query(sqldeletequery)
            return Grimoire.Types.AnnotatedValue(res, 'Deleted row')
        __dir_allowall__ = False # delete.sqlentries can't be called in itself
        def _dir(self, path, depth):
            def unlocked():
                return self._getpath(Grimoire.Types.MethodBase, 1,
                                     ['list', 'sqltables', '$sqlservername'] + path
                                     )([], depth, [1, 0], False)
            return self._callWithUnlockedTree(unlocked)
        def _params(self, path):
            if len(path) != 1:
                raise AttributeError()
            rows = self._callWithUnlockedTree(Grimoire.Types.getValue,
                                              self._getpath(Grimoire.Types.MethodBase, 1,
                                                            ['list', '$sqlentries', '$sqlservername'] + path)())
            paramsList = Ps([('rowid', A(R(types.IntType, rows.list), 'The row to delete'))])
            return A(paramsList,
                     Grimoire.Types.Formattable('Delete entry from table %(table)s', table = path[0])) 
        
