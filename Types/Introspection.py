import string, types, Grimoire.Utils, copy
import Composable, Representation, Derived


class MethodNotImplementedHere(AttributeError):
    """This method is catched during _treeOp calls, and causes the
    search for a method implementation to continue.
    """

class GetpathRoot(object): pass
class TreeRoot(GetpathRoot): pass
class MethodBase(GetpathRoot): pass
class CurrentNode(GetpathRoot): pass


class NoValueType:
    def __cmp__(self, other): return -1
    def __nonzero__(self): return False
NoValue = NoValueType()

class ParamsType(Composable.Composable, Derived.StaticDerivedType):
    description = 'parameter list of'

    def __init__(self, *arg, **kw):
        super(ParamsType, self).__init__(*arg, **kw)
        self.argdict = types.DictType(self.arglist)

    def derive(cls, arglist = [], required = None, resargstype = None, reskwtype = None, convertType = None, name = None, bases = None, dict = None):
        if required is None:
            required = len(arglist)
        return super(ParamsType, cls).derive(
            name, bases,
            Derived.extendDictWithDefaults(dict, {
                'arglist': arglist,
                'required': required,
                'resargstype': resargstype,
                'reskwtype': reskwtype,
                'convertType': convertType}))
    derive = classmethod(derive)
    
    def getTag(cls, name, bases = (), dict = {}, tag = ()):
        convertType = Derived.getDefAttr(bases, dict, 'convertType')
        if convertType:
            convertType = convertType.getTag(convertType.__name__, (convertType,))
        return (tuple(Derived.getDefAttr(bases, dict, 'arglist')),
                Derived.getDefAttr(bases, dict, 'required'),
                Derived.getDefAttr(bases, dict, 'resargstype'),
                Derived.getDefAttr(bases, dict, 'reskwtype'),
                convertType)
    getTag = classmethod(getTag)
    
    def __isInstance__(self, (args, kw)):
        try:
            self.compileArgs(args, kw)
            return 1
        except TypeError:
            return 0
    
    def compileArgs(self, *arg, **kw):
        """#### fixme ####
        description = '''Provided for backwards-compatibility, use
        self.__call__ instead.'''
        #### end ####"""
        return self(*arg, **kw)

    def addDefaults(self, defaults, extendResticted = 1):
        def addDefaultValue((name, type)):
            if name in defaults:
                comment = Composable.getComment(type)
                type = Composable.getValue(type)
                if Grimoire.Utils.isDescendant(type, Derived.ValuedType):
                    restricted = Grimoire.Utils.isDescendant(type, Derived.RestrictedType)
                    resvalues = []
                    try:
                        defaultvalues = defaults[name].values
                    except:
                        defaultvalues = defaults[name]
                    for value in defaultvalues:
                        if extendResticted or not restricted or value in type.values:
                            resvalues.append(value)
                    for value in type.values:
                        if value not in resvalues:
                            resvalues.append(value)
                    class type(type):
                        values = tuple(resvalues)
                else:
                    type = Derived.HintedType.derive(type, defaults[name])
                if comment is not None:
                    type = Composable.AnnotatedValue(type, comment)
            return (name, type)
        class ParamsType(self):
            arglist = map(addDefaultValue, self.arglist)
        return ParamsType

    def removeArgs(self, *args):
        def removeArgs((name, type)):
            if name in args or Grimoire.Utils.isSubclass(type, args):
                raise Grimoire.Grimoire.Utils.FilterOutError()
            return (name, type)
        requiredargs = list(Grimoire.Grimoire.Utils.Map(removeArgs, self.arglist[:self.required]))
        optionalargs = list(Grimoire.Grimoire.Utils.Map(removeArgs, self.arglist[self.required:]))
        class ParamsType(self):
            arglist = requiredargs + optionalargs
            required = len(requiredargs)
        return ParamsType

    def compose_impl(self, composeClass, translationTable):
        def conv(*strs):
            return self.__convert__(composeClass, translationTable, *strs)
        def conv1(str):
            return conv(str)[0]
        resarg = []
        if self.resargstype:
            resarg = ['*arg: ' + conv1(self.resargstype)]
        reskw = []
        if self.reskwtype:
            reskw = ['**kw: ' + conv1(self.reskwtype)]
        opt = [conv1(arg[0]) + ': ' + conv1(arg[1]) for arg in self.arglist[self.required:]]
        res = string.join([conv1(arg[0]) + ': ' + conv1(arg[1]) for arg in self.arglist[:self.required]], ', ')
        if opt or resarg or reskw:
            res += '(' + string.join(opt + resarg + reskw, ', ') + ')'
        return res

class GenericParamsType(Derived.GenericStaticDerivedType):
    __metaclass__ = ParamsType
    arglist = []
    required = None
    resargstype = None
    reskwtype = None
    convertType = None
    def __init__(self, args = [], extraArgs = [], kws = {}, checkTypes = 1, listify = 0, falseAsAbsent = 0, convert = 1):
        """Compiles a set of arguments, that is, either check their
        types, or convert them to the correct types.

        If listify, args contains all required arguments and all
        optional up to the first one not included (any one after that
        one is in kws), otherwize args is empty.

        Exceptions: checkTypes will raise a TypeError for any argument
        of the wrong type.
        """
        if Grimoire.Utils.isInstance(args, GenericParamsType):
            extraArgs = args.extraArgs
            kws = args.kws
            args = args.args
        paramsType = type(self)
        self.args = []
        self.extraArgs = []
        self.kws = {}

        # Put all arguments in the order they will be returned in if listify == 0
        self.kws.update(kws)
        for (name, t), arg in Grimoire.Utils.Zip(paramsType.arglist, args):
            self.kws[name] = arg
        if len(args) > len(paramsType.arglist):
            self.extraArgs = args[len(paramsType.arglist):]
        self.extraArgs += extraArgs
        
        # Check/convert types
        for name in self.kws.keys():
            arg = self.kws[name]
            if name in paramsType.argdict:
                t = paramsType.argdict[name]
            else:
                t = paramsType.reskwtype
            t = Composable.getValue(t)
            if not t:
                raise TypeError('Unknown keyword argument ' + name)
            if not checkTypes:
                try:
                    self.kws[name] = t(arg)
                except Exception, e:
                    if falseAsAbsent and not arg:
                        del self.kws[name]
                    else:
                        raise e
            elif not Grimoire.Utils.isInstance(arg, t):
                raise TypeError('Argument %s %s is not of correct type %s' % (name, Grimoire.Utils.objInfo(arg), Grimoire.Utils.objInfo(t)))
        t = Composable.getValue(paramsType.resargstype)
        argPos = 0
        while argPos < len(self.extraArgs):
            if not paramsType.resargstype:
                raise TypeError('Too many non-keyword arguments')
            arg = self.extraArgs[argPos]
            if not checkTypes:
                try:
                    self.extraArgs[argPos] = t(arg)
                except Exception, e:
                    if falseAsAbsent and not arg:
                        del self.extraArgs[argPos]
                        break
                    else:
                        raise e
            elif not Grimoire.Utils.isInstance(arg, t):
                raise TypeError('Extra non-keyword ergument (' + Grimoire.Utils.objInfo(arg) +
                                ') is not of correct type (' + Grimoire.Utils.objInfo(t) + ')')
            argPos += 1

        if listify or checkTypes:
            for pos in range(0, len(paramsType.arglist)):
                name, t = paramsType.arglist[pos]
                if name not in self.kws:
                    if pos < paramsType.required and checkTypes:
                        raise TypeError('Argument ' + name + ' is required')
                    break
                if listify:
                    self.args += [self.kws[name]]
                    del self.kws[name]

        if convert and paramsType.convertType:
            converted = paramsType.convertType.compileArgs(self, self.args, self.extraArgs, self.kws, 0, listify, falseAsAbsent)
            self.args = converted.args
            self.extraArgs = converted.extraArgs
            self.kws = converted.kws

ParamsType.generic = GenericParamsType

convertParamsToUTF8 = ParamsType.derive(resargstype = Derived.UTF8Type,
                                        reskwtype = Derived.UTF8Type,
                                        convertType = ParamsType.derive(resargstype = types.StringType,
                                                                        reskwtype = types.StringType))
