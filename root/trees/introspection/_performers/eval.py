import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, Grimoire.Utils.Serialize.Reader, Grimoire.Utils.Serialize.Types, types


Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class methodOfExpression(Grimoire.Performer.Method):
        def _call(self, expr, simpleExpressionOnly = False):
            if Grimoire.Utils.isInstance(expr, types.BaseStringType):
                expr = Grimoire.Utils.Serialize.Reader.read(Grimoire.Utils.Serialize.Reader.Buffer(str(expr))) # FIXME: Bufer should really do the conversion to utf-8 by itself!
            res = []
            while (Grimoire.Utils.isInstance(expr, Grimoire.Utils.Serialize.Types.Extension)
                   and expr.value[0] is not Grimoire.Utils.Serialize.Types.Identifier):
                if expr.value[0] is Grimoire.Utils.Serialize.Types.Member:
                    (expr, member) = expr.value[1]
                    if (    Grimoire.Utils.isInstance(member, Grimoire.Utils.Serialize.Types.Extension)
                        and member.value[0] is Grimoire.Utils.Serialize.Types.Identifier):
                        res.append(member.value[1])
                    else:
                        if simpleExpressionOnly:
                            raise Exception("Not simple")
                        res = []
                elif expr.value[0] is Grimoire.Utils.Serialize.Types.Application:
                    if simpleExpressionOnly:
                        raise Exception("Not simple")
                    expr = expr.value[1][0]
                    res = []
                else:
                    raise Exception('Expression does not have a method')
            if not Grimoire.Utils.isInstance(expr, Grimoire.Utils.Serialize.Types.Extension) or expr.value[1] != '_':
                raise Exception('Expression does not have a method')
            res.reverse()
            return res
        def _params(self):
            return A(Ps([('expr', A(Grimoire.Types.NonemptyStringType,
                                    'Grimoire expression to execute'))]),
                     'Extracts the main (first) method of a Grimoire expression')
        
    class eval(Grimoire.Performer.Method):
        def _call(self, expr):
            if Grimoire.Utils.isInstance(expr, types.BaseStringType):
                expr = Grimoire.Utils.Serialize.Reader.read(Grimoire.Utils.Serialize.Reader.Buffer(expr))

            def prepareTree(obj):
                return Grimoire.Performer.Logical(Grimoire.Types.getValue(obj))

            def evaluate(type, value):
                if type is Grimoire.Utils.Serialize.Types.Identifier and value == '_':
                    #### fixme ####
                    # description = """This means that _.foo.bar._.fie
                    # will give an error, that is, a single underscore
                    # can not be used as a method path element
                    # name!"""
                    #### end ####
                    return self._getpath(Grimoire.Types.TreeRoot)
                elif type is Grimoire.Utils.Serialize.Types.Member:
                    (obj, member) = value
                    if (    Grimoire.Utils.isInstance(member, Grimoire.Utils.Serialize.Types.Extension)
                        and member.value[0] is Grimoire.Utils.Serialize.Types.Identifier):
                        member = member.value[1]
                    return getattr(prepareTree(obj), member)
                elif type is Grimoire.Utils.Serialize.Types.Application:
                    (method, params) = value
                    def getArgs(param):
                        if (    Grimoire.Utils.isInstance(param, Grimoire.Utils.Serialize.Types.Extension)
                            and param.value[0] is Grimoire.Utils.Serialize.Types.ParameterName):
                            raise Grimoire.Utils.FilterOutError()
                        return param
                    def getKw(param):
                        if (    Grimoire.Utils.isInstance(param, Grimoire.Utils.Serialize.Types.Extension)
                            and param.value[0] is Grimoire.Utils.Serialize.Types.ParameterName):
                            return param.value[1]
                        raise Grimoire.Utils.FilterOutError()
                    return prepareTree(method)(*Grimoire.Utils.Map(getArgs, params),
                                               **dict(Grimoire.Utils.Map(getKw, params)))
                else:
                    return Grimoire.Utils.Serialize.Types.Extension(type, value)

            return Grimoire.Utils.Serialize.Reader.extend(expr, evaluate)

        def _params(self):
            return A(Ps([('expr', A(Grimoire.Types.NonemptyStringType,
                                    'Grimoire expression to execute'))]),
                     'Applies a Grimoire expression on the tree')
