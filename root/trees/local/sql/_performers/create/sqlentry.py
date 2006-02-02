import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, string, types, stat, os, pg

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive
R = Grimoire.Types.RestrictedType


def getTableParams(tree, table):
    def excludeSerials(param):
        if Grimoire.Utils.isSubclass(Grimoire.Types.getValue(param[1]), Grimoire.Types.SerialType):
            raise Grimoire.Utils.FilterOutError()
        return param
    return Ps(Grimoire.Utils.Map(
        excludeSerials,
        Grimoire.Utils.getpath(tree.list.columntype, ['$sqlservername', table])([])), 0)

def getTableConvertingParams(tree, table):
    class ParamsType(getTableParams(tree, table)):
        convertType = Grimoire.Types.convertParamsToUTF8
    return ParamsType
getTableConvertingParams = Grimoire.Utils.cachingFunction(getTableConvertingParams)

class Performer(Grimoire.Performer.Base):
    class sqlentry(Grimoire.Performer.SubMethod):
        __path__ = ['$sqlentry', '$sqlservername']
        def _call(self, path, *arg, **kws):
            if len(path) != 1:
                raise AttributeError()
            kws = self._callWithUnlockedTree(getTableConvertingParams, self._getpath(Grimoire.Types.MethodBase, 1), path[0]).compileArgs(arg, [], kws).kws
            def unlocked():
                return self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(['local', 'sql', 'db'], None)
            dbconn = self._callWithUnlockedTree(unlocked)
            def convertArg(arg):
                if type(arg) == types.StringType:
                    return '\''+arg+'\''
                else:
                    return str(arg)
            query = 'insert into "'+path[0]+'" ("'+string.join(kws.keys(), '","')+'") values ('+string.join(map(convertArg, kws.values()), ',')+')'
            resnr = dbconn.query(query)
            # Uses the postgres specific OID 'column' - probably not portable.
            # However, the portable "insert" call didn't work with columns with reserved names, even when
            # the names in the dict were quoted with ":s, so we had to use a raw query instead, and this
            # only returns the OID number. 
            res = self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 1, ['list', 'nonpath', '$sqlentries', '$sqlservername']
                                      )(tables = [path[0]], where = """"oid" = '%s'""" % resnr))
            return Grimoire.Types.AnnotatedValue(res, 'Inserted row')
        __dir_allowall__ = False # create.sqlentries can't be called in itself
        def _dir(self, path, depth):
            def unlocked():
                return self._getpath(Grimoire.Types.MethodBase, 1,
                                     ['list', 'sqltables', '$sqlservername'] + path
                                     )([], depth, isMethodList = [1, 0], listViews = False)
            return self._callWithUnlockedTree(unlocked)
        def _params(self, path):
            if len(path) != 1:
                raise AttributeError()
            return A(self._callWithUnlockedTree(getTableParams, self._getpath(Grimoire.Types.MethodBase, 1), path[0]),
                     Grimoire.Types.Formattable('Insert values into table %(table)s', table = path[0]))
