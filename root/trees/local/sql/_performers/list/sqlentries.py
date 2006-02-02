import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, string, types, stat, os, pg
import Grimoire.root.trees.local.sql._performers.type

debugSqlQuery = False

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive
R = Grimoire.Types.RestrictedType.derive

NES = Grimoire.Types.NonemptyStringType

class AnyValueType:
    def __cmp__(self, other):
        return -1
AnyValue = Grimoire.Types.AnnotatedValue(AnyValueType(),
                                        'Any')

def getListSqlentriesParams(tree, table):
    def onlyReferences(param):
        if not Grimoire.Utils.isSubclass(Grimoire.Types.getValue(param[1]),
                                         Grimoire.root.trees.local.sql._performers.type.GenericReferenceType):
            raise Grimoire.Utils.FilterOutError()
        refType = Grimoire.Types.getValue(param[1])
        return param
    return Ps(
              Grimoire.Utils.Map(onlyReferences,
                                 Grimoire.Utils.getpath(tree.columntype, ['$sqlservername', table])([])) + 
              [('orderBy', A(NES, 'A list of columns to sort the answers by')),
               ('orderWay', A(R(types.IntType,
                                [A(0, 'Ascending'), A(1, 'Descending')]), 'The way to order the sort, if sort is called for')),
               ('distinct', A(R(types.IntType, [A(0, 'All answers'), A(1, 'Only distinct')]), 'Show'))],
              0)
getListSqlentriesParams = Grimoire.Utils.cachingFunction(getListSqlentriesParams)


class Performer(Grimoire.Performer.Base):
    class sqltables(Grimoire.Performer.SubMethod):
        __path__ = ['sqltables', '$sqlservername']
        def _call(self, path, prefix = [], depth = Grimoire.Performer.UnlimitedDepth, isMethodList = [1, 1], listViews = True):
            dp = depth
            if dp < 0:
                dp = Grimoire.Performer.UnlimitedDepth
            columns = ['"table"', '"column"']
            pathlen = len(path)
            methodlen = 2 * isMethodList[1] or isMethodList[0]
            columnsend = min(pathlen + dp, len(columns), methodlen)
            pathprefix = path + prefix
            def unlocked():
                return self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(['local', 'sql', 'db'], None)
            dbconn = self._callWithUnlockedTree(unlocked)
            def mangleRow(row):
                row = row[:-1]
                while row and row[-1] is None: row = row[:-1]
                return (isMethodList[pathlen + len(row) - 1], list(row))

            if not listViews:
                viewsWhere = [" view is not True "]
            else:
                viewsWhere = []
            query = "select distinct %(columns)s from metainfo where %(wheres)s" % {
                               'columns': string.join(columns[len(path):columnsend] + ["1"], ', '),
                               'wheres': string.join(
                                   ["%(column)s = '%(value)s'" % {'column': column, 'value': value}
                                    for column, value in Grimoire.Utils.Zip(columns, pathprefix)] +
                                   viewsWhere + 
                                   ['true'], ' and ')}

            return map(mangleRow,
                       dbconn.query(
                           query).getresult())
        def _dir(self, path, depth):
            return [(1, [])]
        def _params(self, path):
            return Grimoire.Types.AnnotatedValue(
                Grimoire.Types.ParamsType.derive(
                    [('prefix',
                      Grimoire.Types.AnnotatedValue(
                          Grimoire.Types.StringListType,
                          "Only return entries under")),
                     ('depth',
                      Grimoire.Types.AnnotatedValue(
                          types.IntType,
                          "Only return entries this far down in the tree (-1 means infinity)")),
                     ('isMethodList',
                      Grimoire.Types.AnnotatedValue(
                          Grimoire.Types.ListType.derive(types.IntType),
                          "Levels that are methods (default is all). Should be a list of 1:s and 0s of length 2")),
                     ],
                    0),
                Grimoire.Types.Formattable(
                    'List SQL tables under %(path)s',
                    path=path))

    class sqlrows(Grimoire.Performer.SubMethod):
        __path__ = ['sqlrows', '$sqlservername']
        def _call(self, path, where = 'true'):
            if len(path) != 1:
                raise AttributeError(path)
            table = path[0]
            dbconn = self._callWithUnlockedTree(lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(['local', 'sql', 'db'], None))
            fmt = self._callWithUnlockedTree(lambda: Grimoire.Types.getComment(
                self._getpath(Grimoire.Types.MethodBase,
                              path=['columntype', '$sqlservername', table]
                              )()))
            paramnames = Grimoire.Utils.SortedList(Grimoire.Types.Formattable(fmt).getFormatParams())
            paramtables = {}
            exprcolumns = []
            for param in paramnames:
                path = param.split('.')
                if len(path) == 1:
                    expr = '"%(table)s"."%(column)s"' % {'table': table, 'column': path[0]}
                    paramtables[param] = table
                else:
                    pth = [table] + path[:-1]
                    pthlen = len(pth)
                    def pr(x):
                        if debugSqlQuery:
                            print x
                        return x
                    reftables = [table] + list(dbconn.query(pr(
                        "select %(references)s from %(tables)s where %(wheres)s" % {
                            'references': string.join(['m%s."references"' % str(n) for n in xrange(0, pthlen - 1)], ', '),
                            'tables': string.join(['metainfo as m%s' % str(n) for n in xrange(0, pthlen - 1)], ', '),
                            'wheres': string.join(['m0."table" = \'%s\' and m0."column" = \'%s\'' % (pth[0], pth[1])] +
                                                  ['m%s."table" = m%s."references" and m%s."column" = \'%s\'' % (n - 1, n - 2, n - 1, pth[n])
                                                   for n in xrange(2, pthlen)],
                                                  ' and ')})).getresult()[0])
                    expr = '(select "%(lasttable)s"."%(lastattr)s" from %(tables)s where %(wheres)s)' % {
                        'lasttable': reftables[-1],
                        'lastattr': path[-1],
                        'tables': string.join(map(lambda x: '"%s"' % x, reftables[1:]), ', '),
                        'wheres': string.join(
                        Grimoire.Utils.Map(lambda x: '"%s"."%s" = "%s"."id"' % x,
                                           Grimoire.Utils.Zip(reftables, path[:-1], reftables[1:])),
                            ' and ')}
                    paramtables[param] = reftables[-1]
                exprcolumns += ['%(expr)s as "%(param)s"' % {
                        'expr': expr,
                        'param': param,
                    }]
            def returnLine(line):
                def convertType(param, value):
                    def unlocked():
                        return (param,
                            Grimoire.Types.getValue(
                                self._getpath(Grimoire.Types.MethodBase,
                                              path=['columntype', '$sqlservername', paramtables[param], param.split('.')[-1]]
                                              )()
                                )(value))
                    return self._callWithUnlockedTree(unlocked)
                str = Grimoire.Types.Formattable(
                        fmt,
                        **dict(Grimoire.Utils.Map(
                            convertType,
                            paramnames, line[1:])))
                return Grimoire.Types.AnnotatedValue(line[0], str)
            return map(
                returnLine,
                dbconn.query(
                    """select %(columns)s from "%(table)s" where %(wheres)s;""" % {
                        'table': table,
                        'columns': string.join(['"id"'] + exprcolumns, ', '),
                        'wheres': where
                    }).getresult())
        
        def _dir(self, path, depth):
            if depth == 0:
                return [(0, ['list'])]
            return self._getpath(Grimoire.Types.MethodBase,
                                 path=['sqltables', '$sqlservername'] + path
                                 )([], depth, [1, 0])
        def _params(self, path):
            return A(
                Ps([('where', A(types.StringType, 'SQL where clause'))], 2),
                "List rows in a table formatted in a user-friendly way")

    class nonpath_sqlentries(Grimoire.Performer.Method):
        __path__ = ['nonpath', '$sqlentries', '$sqlservername']
        def _call(self, tables = [], columns = [], where = 'true', orderBy = None, orderWay = 0, distinct = 0, prettyPrint = True):
            if prettyPrint and not columns:
                # FIXME: Handle where clauses (that references several tables) correctly
                # Show the whole shebang
                res = []
                for table in tables:
                    res.extend(self._getpath(Grimoire.Types.MethodBase,
                                             path=['sqlrows', '$sqlservername', table]
                                             )(where))
                return Grimoire.Types.Lines(*res)
            sqlexpr = 'select %(columns)s from %(tables)s' % {
                'tables': string.join(tables, ', '),
                'columns': columns and ', '.join(['.'.join(['"%s"' % part for part in column]) for column in columns]) or '*'}
            sqlexpr += ' where %s' % where
            if orderBy is not None:
                sqlexpr += ' order by %s' % orderBy
            sqlexpr += ';'
            res = self._callWithUnlockedTree(
                lambda : self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                    ['local', 'sql', 'db'], None
                    ).query(sqlexpr).getresult())
            if prettyPrint:
                filledcolumns = [len(column) > 1 and column or type(column)((tables[0],)) + column for column in columns]
                columns = self._callWithUnlockedTree(lambda: getattr(self._getpath(Grimoire.Types.MethodBase).columntypes, '$sqlservername')(filledcolumns))
            def mangleRow(row):
                res = Grimoire.Utils.Zip(columns, row)
                if prettyPrint:
                    return Grimoire.Types.Lines(*map(lambda (col, coldata): A(coldata, Grimoire.Types.getComment(col[1])), res))
                else:
                    return tuple(res)
            res = map(mangleRow, res)
            if prettyPrint:
                res = Grimoire.Types.Paragraph(*res)
            return res
        def _params(self):
            return A(
                Ps([('tables', A(NES, 'List of tables to query')),
                    ('columns', A(NES, 'List of columns to query')),
                    ('where', A(NES, 'A \"where\" clause to an SQL select query, to select the rows from the table')),
                    ('orderBy', A(NES, 'A list of columns to sort the answers by')),
                    ('orderWay', A(R(types.IntType,
                                     [A(0, 'Ascending'), A(1, 'Descending')]), 'The way to order the sort, if sort is called for')),
                    ('distinct', A(R(types.IntType, [A(0, 'All answers'), A(1, 'Only distinct')]), 'Show')),
                    ('prettyPrint', A(R(types.IntType, [A(1, 'Pretty-printed text'), A(0, 'Python lists')]), 'Return'))], 2),
                "Execute an SQL query against a Postgres SQL server")

    class sqlentries(Grimoire.Performer.SubMethod):
        __path__ = ['$sqlentries', '$sqlservername']
        def _call(self, path, *arg, **kws):
            kws = self._callWithUnlockedTree(getListSqlentriesParams, self._getpath(Grimoire.Types.MethodBase), path[0]).compileArgs(arg, [], kws).kws
            reskws = {}
            wherekws = {}
            for key in kws.iterkeys():
                if key in ('orderBy', 'orderWay', 'distinct'):
                    reskws[key] = kws[key]
                else:
                    wherekws[key] = kws[key]
            if wherekws:
                reskws['where'] = ' and '.join([""""%s" = '%s'""" % item for item in wherekws.iteritems()])
            def unlocked():
                return self._getpath(Grimoire.Types.MethodBase,
                                     path=['nonpath', '$sqlentries', '$sqlservername']
                                     )([path[0]], **reskws)
            return self._callWithUnlockedTree(unlocked)

        __dir_allowall__ = False # list.sqlentries can't be called in itself
        __dir_exclude__ = (['sqltables'],)
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase,
                                      path=['sqltables', '$sqlservername'] + path
                                      )([], depth, isMethodList=[1, 0]))
        def _params(self, path):
            return A(self._callWithUnlockedTree(getListSqlentriesParams, self._getpath(Grimoire.Types.MethodBase), path[0]),
                     Grimoire.Types.Formattable('List entries from table %(table)s', table = path[0]))
