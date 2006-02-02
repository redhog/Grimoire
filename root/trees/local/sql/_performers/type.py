import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, types, string, StringIO
import Grimoire.Utils.Serialize.Writer, Grimoire.Utils.Serialize.Reader, Grimoire.Utils.Serialize.RPC

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive
                
class ReferenceType(Grimoire.Types.RestrictedType):
    description = "reference to"
    def derive(cls, table, values = (), name = None, bases = None, dict = None):
        d = Grimoire.Types.extendDictWithDefaults(dict, {'table':table})
        return super(ReferenceType, cls).derive(None, values, name, bases, d)
    derive = classmethod(derive)
    def getTag(cls, name, bases = (), dict = {}, tag = ()):
        # Yes, this is correct, we want to avoid putting values from SQL into the tag. Values are just cached here...
        return super(Grimoire.Types.ValuedType, cls).getTag(name, bases, dict, (Grimoire.Types.getDefAttr(bases, dict, 'table'),) + tag)
    getTag = classmethod(getTag)

# FIXME: Remove inheritance of types.IntType when DerivedType can
# handle parentType set in the geric class
class GenericReferenceType(Grimoire.Types.GenericRestrictedType, types.IntType):
    __metaclass__ = ReferenceType
    parentType = types.IntType
    table = None
ReferenceType.generic = GenericReferenceType

class ReferenceTypeType:
    typeName = 'ReferenceType'
    type = ReferenceType

    def __init__(self, tree):
        self.tree = tree

    def serialize(self, obj):
        return obj.table

    def parse(self, typeName, table):
        return ReferenceType.derive(
            table,
            Grimoire.Utils.getpath(self.tree.list.sqlrows, ['$sqlservername', table])())

class Performer(Grimoire.Performer.Base):
    class list_columntype(Grimoire.Performer.SubMethod):
        __path__ = ['list', 'columntype', '$sqlservername']
        def _call(self, path, columns = None):
            table = None
            cols = columns
            if path:
                table = path[0]
                if path[1:]:
                    if cols is not None:
                        raise ValueError('Columns can not be specified both in path and in an argument')
                    cols = [path[1]]
                    if path[2:]:
                        raise AttributeError('Path to long')
            if table is None and cols is not None:
                raise AttributeError('Columns must be specified within a table')
            dbconn = self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(['local', 'sql', 'db'], None))

            def pr(x):
                print x
                return x
            res = dbconn.query(pr(
                'select "column", "type", "description" from metainfo where ' +
                ((table and "\"table\" = '" + table + "'") or '"table" is null') +
                ' and ' +
                (   (cols and '(' + string.join(["\"column\" = '%s'" % column for column in cols], ' or ') + ')')
                 or (cols is None and '"column" is null')
                 or '"column" is not null order by number'))).getresult()
            if not res:
                raise AttributeError('No such table or column', path)
            res = map(
                lambda (column, type, description):
                    (column,
                     A((type and getattr(self._getpath(Grimoire.Types.MethodBase).type.deserialize, '$sqlservername')(type)) or type,
                       description)),
                res)
            if columns is None:
                return res[0][1]
            return res

        def _dir(self, path, depth):
            return self._getpath(Grimoire.Types.MethodBase,
                                 ['list', 'sqltables', '$sqlservername'] + path
                                 )([], depth)
        
        def _params(self, path):
            return Ps()

    class list_columntypes(Grimoire.Performer.Method):
        __path__ = ['list', 'columntypes', '$sqlservername']
        def _call(self, columns = []):
            tablecolumns = {}
            for column in columns:
                if column[0] not in tablecolumns:
                    tablecolumns[column[0]] = []
                tablecolumns[column[0]].append(column[1])
            for table in tablecolumns.iterkeys():
                tablecolumns[table] = self._getpath(levels=2,
                                                    path=['columntype', '$sqlservername', table]
                                                    )(tablecolumns[table])
            columntypes = []
            for column in columns:
                columntypes.append((column, tablecolumns[column[0]][0][1]))
                del tablecolumns[column[0]][0]
            return columntypes
        
        def _params(self):
            return A(Ps([('columns', A(Grimoire.Types.ListType.derive(Grimoire.Types.UnicodeList), 'Table-column pairs'))]),
                     'List types for columns from several tables simultaneously')

    class type_serialize(Grimoire.Performer.Method):
        __path__ = ['type', 'serialize', '$sqlservername']
        def _call(self, type):
            res = StringIO.StringIO()
            Grimoire.Utils.Serialize.Writer.write(
                res,
                Utils.Serialize.Writer.contract(
                    type,
                    Grimoire.Utils.Serialize.RPC.ObjectMappedExtension(
                        Grimoire.Utils.Serialize.RPC.stdObjectMap() +
                        [ReferenceTypeType(self._getpath(Grimoire.Types.MethodBase))]).serialize))
            return res.getvalue()

        def _params(self):
            return A(Ps([('type', A(Grimoire.Types.AnyType, 'The type to serialize'))]),
                     "Serializes a type to a string")

    class type_deserialize(Grimoire.Performer.Method):
        __path__ = ['type', 'deserialize', '$sqlservername']
        def _call(self, type):
            return Grimoire.Utils.Serialize.Reader.extend(
                Grimoire.Utils.Serialize.Reader.read(
                    Grimoire.Utils.Serialize.Reader.Buffer(type)),
                Grimoire.Utils.Serialize.RPC.ObjectMappedExtension(
                    Grimoire.Utils.Serialize.RPC.stdObjectMap() +
                    [ReferenceTypeType(self._getpath(Grimoire.Types.MethodBase))]).parse)

        def _params(self):
            return A(Ps([('type', A(types.StringType, 'String representation of type to deserialize'))]),
                     "Deserializes a type from a string")
