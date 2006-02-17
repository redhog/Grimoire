import Grimoire.Utils, Types, string, types, re, sys, traceback

debugExceptions = 0

def writeList(f, obj, sep = ', ', writelast = False):
    first = True
    for objpart in obj:
        if not first:
            f.write(sep)
        write(f, objpart)
        first = False
    if writelast:
        f.write(sep)

__identifierre      = re.compile('([.,:=<{\[\(\)\]}>\\\\' + string.whitespace + '])')
__identifierstartre = re.compile('([.,:=<{\[\(\)\]}>\\\\' + string.whitespace + '0-9])')
def write(f, obj):
    t = type(obj)
    if t == types.ListType:
        f.write('[')
        writeList(f, obj)
        f.write(']')
    elif t == types.TupleType:
        f.write('(')
        writeList(f, obj, writelast = True)
        f.write(')')
    elif t in (types.DictType, types.DictProxyType):
        f.write('{')
        first = 1
        for key, value in obj.iteritems():
            if not first:
                f.write(', ')
            first = 0
            write(f, key)
            f.write(': ')
            write(f, value)
        f.write('}')
    elif t == types.UnicodeType:
        f.write('u')
        f.write(repr(obj.encode('utf-8')))
    elif t in (types.NoneType, types.BooleanType, types.StringType, types.FloatType, types.IntType, types.LongType):
        f.write(repr(obj))
    elif t == types.InstanceType and isinstance(obj, Types.Extension):
        value = obj.value
        if value[0] is Types.Identifier:
            f.write(re.sub(__identifierstartre, '\\\\\\1', value[1][0]) +
                    re.sub(__identifierre, '\\\\\\1', value[1][1:]))
        elif value[0] is Types.Member:
            writeList(f, value[1], '.', False)
        elif value[0] is Types.Application:
            write(f, value[1][0])
            f.write('(')
            writeList(f, value[1][1])
            f.write(')')
        elif value[0] is Types.ParameterName:
            writeList(f, value[1], '=', False)
        else:
            f.write('<')
            writeList(f, obj.value)
            f.write('>')
    else:
        raise Types.UnserializableError(obj)
    

def contractList(obj, extension):
    return [contract(objpart, extension) for objpart in obj]

def contractSimple(obj, extension = None):
    t = type(obj)
    if t == types.ListType:
        return contractList(obj, extension)
    elif t == types.TupleType:
        return tuple(contractList(obj, extension))
    elif t in (types.DictType, types.DictProxyType):
        res = {}
        for key, value in obj.iteritems():
            res[contract(key, extension)] = contract(value, extension)
        return res
    elif t in (types.NoneType, types.BooleanType, types.StringType, types.UnicodeType, types.FloatType, types.IntType, types.LongType):
        return obj
    elif t == types.InstanceType and isinstance(obj, Types.Extension):
        return Types.Extension(*contractList(obj.value, extension))
    else:
        raise Types.UnserializableError(obj)

def contract(obj, extension = None):
    try:
        return contractSimple(obj, extension)
    except:
        if not extension:
            t, v, tr = sys.exc_info()
            raise t, v, tr
        if debugExceptions:
            traceback.print_exc()
        return contract(extension(obj), extension)
