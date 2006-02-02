import Grimoire.Utils, Types, string, types, unicodedata, sys, traceback

debugRead = 0
debugInput = 0
debugExceptions = 0

try:
    import psyco
    havePsyco = True
except ImportError:
    havePsyco = False

try:
    from CReader import *
except ImportError:
    from PyReader import *


class NoTransformation(Exception): pass

def internalExtend(expression, extension):
    noTransformation = 1
    if isinstance(expression, (types.ListType, types.TupleType)):
        parts = expression
    elif isinstance(expression, types.DictionaryType):
        parts = Grimoire.Utils.Flatten(expression.iteritems())
    elif isinstance(expression, Types.Extension):
        parts = expression.value
        noTransformation = 0
    else:
        raise NoTransformation()

    res = []
    for part in parts:
        try:
            res.append(internalExtend(part, extension))
            noTransformation = 0
        except NoTransformation:
            res.append(part)
    if noTransformation:
        raise NoTransformation()

    if isinstance(expression, types.TupleType):
        res = tuple(res)
    elif isinstance(expression, types.DictionaryType):
        res = dict(Grimoire.Utils.Zip(
            Grimoire.Utils.Each(res, 2),
            Grimoire.Utils.Each(res[1:], 2)))
    elif isinstance(expression, Types.Extension):
        res = extension(*res)
    return res

    
def extend(expression, extension):
    try:
        return internalExtend(expression, extension)
    except NoTransformation:
        return expression

if havePsyco:
    psyco.bind(internalExtend)
    psyco.bind(extend)
