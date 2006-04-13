import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, types, sys
import FunFormKit.Field, FunFormKit.Form, traceback


debugTypes = 0
debugMethods = 1

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class VerifyField(FunFormKit.Field.VerifyField):
    """Bugfix for FunFormKit.Field.VerifyField."""
    def __init__(self, name, fieldClass,
                 fieldArgs1=None, fieldKW1=None,
                 fieldArgs2=None, fieldKW2=None,
                 **kw):
        fieldArgs1 = fieldArgs1 or ()
        fieldKW1 = fieldKW1 or {}
        fieldArgs2 = fieldArgs2 or ()
        fieldKW2 = fieldKW2 or {}
        formValidators = list(kw.setdefault('formValidators', []))
        formValidators.append(FunFormKit.Field.Validator.FieldsMatch([name, 'verify']))
        print formValidators
        kw['formValidators'] = formValidators
        password = fieldClass(name, *fieldArgs1, **fieldKW1)
        verify = fieldClass('verify', *fieldArgs2, **fieldKW2)
        FunFormKit.Field.CompoundField.__init__(self, name, [password, verify], **kw)

class Performer(Grimoire.Performer.Base):
    class funformkit_result(Grimoire.Performer.Method):
        def _call(performer):
            class Result:
                def __init__(self, result = None, error = None):
                    self.result = result
                    self.error = error
            return Result
        _call = Grimoire.Utils.cachingFunction(_call)
        def _params(self):
            return A(Ps(),
                     'Container class for results')
    class funformkit_formservlet(Grimoire.Performer.Method):
        def _call(performer):
            Result = performer._callWithUnlockedTree(lambda: performer._getpath(levels=1).result())
            
            def argValues2Selections(argvalues, composer, optional = False):
                """Transforms a list of allowed values (from a ValuedType) into a
                "selection" list suitable for FunFormKit.Field.SelectField, i.e. a
                list of pairs of values and their respective comments.
                """
                res = [(num, composer(Grimoire.Types.getComment(argvalue, argvalue)))
                       for (num, argvalue) in enumerate(argvalues)]
                if optional:
                    res.insert(0, (-1, composer('*No value specified*')))
                return res

            def PasswordVerifyField(name, **kw):
                return VerifyField(name, FunFormKit.Field.PasswordField, **kw)

            class ParamTypeValidator(FunFormKit.Validator.ValidatorConverter):
                """A FunFormKit validator that validates against a
                paramsTypeObject.
                """

                def __init__(self, argType, required, composer, **kw):
                    FunFormKit.Validator.ValidatorConverter.__init__(self, **kw)
                    self.required = required
                    self.argType = argType
                    self.composer = composer

                def validate(self, value):
                    try:
                        value = self.convert(value)
                        self.argType(value)
                        return None
                    except Exception, e:
                        if debugTypes:
                            print Grimoire.Utils.objInfo(e)
                            traceback.print_exc()
                        if not self.required and (not value or not value.strip()):
                            return None
                        return self.message('notCorrectType', self.composer(e))

                def convert(self, value):
                    if Grimoire.Utils.isDescendant(self.argType, Grimoire.Types.BooleanType):
                        return (value == 'on')
                    elif Grimoire.Utils.isDescendant(self.argType, Grimoire.Types.Ability.List):
                        def str2pair(str):
                            type, path = str.split(':', 1)
                            type = type.strip().lower()
                            path = path.strip()
                            if not type:
                                raise Exception(type + ' is not a correct type (Allow, Deny or Ignore)')
                            elif type[0] == 'a':
                                type = Grimoire.Types.Ability.Allow
                            elif type[0] == 'd':
                                type = Grimoire.Types.Ability.Deny
                            elif type[0] == 'i':
                                type = Grimoire.Types.Ability.Ignore
                            else:
                                raise Exception(type + ' is not a correct type (Allow, Deny or Ignore)')
                            return (type, path.split('.'))
                        return map(str2pair, value.split(','))
                    elif Grimoire.Utils.isDescendant(self.argType, Grimoire.Types.RestrictedType):
                        value = int(value)
                        if value < 0:
                            return Grimoire.Types.NoValue
                        return Grimoire.Types.getValue(self.argType.getValues()[value])
                    return value

            def paramsTypeObjectToFormFields(typeObj, composer):
                """Transforms a paramsTypeObject into a list of FunFormKit
                FormFields suitable for input to the described function.
                """

                formDef = []
                defaults  = {}
                argnum = 0

                for argpos in range(0, len(typeObj.arglist)):
                    name, argtype = typeObj.arglist[argpos]
                    comment = Grimoire.Types.getComment(argtype, name)
                    argtype = Grimoire.Types.getValue(argtype)

                    klass = None
                    klassArg = {'name':name,
                                'description': composer(comment),
                                'required': argnum < typeObj.required,
                                'validators': [ParamTypeValidator(argtype, argpos < typeObj.required, composer)]}

                    argvalues = []
                    while 1:
                        if Grimoire.Utils.isDescendant(argtype, Grimoire.Types.HintedType):
                            argvalues += argtype.getValues()
                            argtype = argtype.parentType

                        elif Grimoire.Utils.isDescendant(argtype, Grimoire.Types.NonemptyType):
                            argtype = argtype.parentType

                        elif argtype is Grimoire.Types.AnyType or Grimoire.Utils.isDescendant(argtype, Grimoire.Types.ListType):
                            argtype = types.StringType
                            argvalues = map(repr, argvalues)
                            break
                        else:
                            break

                    defaults[name] = None
                    if argvalues:
                        defaults[name] = Grimoire.Types.getValue(argvalues[0])

                    if Grimoire.Utils.isDescendant(argtype, Grimoire.Types.RestrictedType):
                        klass = FunFormKit.Field.SelectField
                        klassArg['selections'] = argValues2Selections(argtype.getValues(), composer, argpos >= typeObj.required)

                    elif Grimoire.Utils.isDescendant(argtype, Grimoire.Types.BitfieldType):
                        klass = FunFormKit.Field.MultiSelectField
                        klassArg['selections'] = argValues2Selections(argtype.values, composer)
                        defaults[name] = map(Grimoire.Types.getValue, argvalues)

                    elif Grimoire.Utils.isDescendant(argtype, Grimoire.Types.BooleanType):
                        klass = FunFormKit.Field.CheckboxField

                    elif Grimoire.Utils.isDescendant(argtype, Grimoire.Types.LoseNewPasswordType):
                        klass = PasswordVerifyField
                        klassArg['fieldKW1'] = {'size': 10, 'description': 'Once', 'validators': klassArg['validators']}
                        klassArg['fieldKW2'] = {'size': 10, 'description': 'Again'}

                    elif Grimoire.Utils.isDescendant(argtype, Grimoire.Types.LosePasswordType):
                        klass = FunFormKit.Field.PasswordField
                        klassArg['size'] = 10

                    elif Grimoire.Utils.isDescendant(argtype,
                                                     types.StringType,
                                                     types.IntType,
                                                     types.UnicodeType,
                                                     Grimoire.Types.UsernameType,
                                                     Grimoire.Types.Ability.List):
                        klass = FunFormKit.Field.TextField
                        klassArg['size'] = 10

                    else:
                        raise Exception("Unable to render input field for unknown type " + Grimoire.Utils.objInfo(typeObj.arglist[argpos][1]))

                    formDef += [klass(**klassArg)]
                    argnum += 1
                return (formDef, defaults)


            def paramsTypeObjectToForm(name, *arg, **kw):
                """Transforms a paramsTypeObject into a list of FunFormKit
                Form suitable for input to the described function.
                """

                formDef, defaults = paramsTypeObjectToFormFields(*arg, **kw)
                return (FunFormKit.Form.FormDefinition(
                            '',
                            formDef +
                            [FunFormKit.Field.SubmitButton(name='submit',
                                                           description='Okay')],
                            name = name),
                        defaults)

            class FormServlet(FunFormKit.Form.FormServlet):
                def __init__(self, *arg, **kw):
                    FunFormKit.Form.FormServlet.__init__(self, *arg, **kw)
                    self._formDefinitions = {}
                    self._defaults = {}
                    self._params = {}
 
                def createForm(self, method):
                    if method is not None:
                        methodName = performer._callWithUnlockedTree(lambda: performer._getpath(Grimoire.Types.MethodBase, 1).urlname.method2name(method))
                        if methodName not in self._formDefinitions:
                            self._params[method] = self.getParams(method)
                            if not Grimoire.Types.getComment(self._params[method]) and \
                               not len(Grimoire.Types.getValue(self._params[method]).arglist):
                                return None
                            else:
                                self._formDefinitions[methodName], self._defaults[method] = paramsTypeObjectToForm(
                                    methodName,
                                    Grimoire.Types.getValue(self._params[method]),
                                    self.getComposer(method))
                        return (self._formDefinitions[methodName], self._defaults[method])
                    return None

                def getParams(self, method):
                    raise NotImplemented

                def getFn(self, method):
                    raise NotImplemented

                def getComposer(self, *arg, **kw):
                    raise NotImplemented

                def handleCall(self, method, data):
                    # FIXME: Implemented in the base-client, remove from here
                    fn = self.getFn(method)
                    args = Grimoire.Types.getValue(
                        self._params[method]).compileArgs([], [], data, 0, 1, 1)
                    result = Result()
                    try:
                        result.result = fn(*(args.args + args.extraArgs),
                                           **args.kws)
                    except:
                        result.error = sys.exc_info()[1]
                        if debugMethods:
                            traceback.print_exc()
                    return result
            return FormServlet
        _call = Grimoire.Utils.cachingFunction(_call)
        def _params(self):
            return A(Ps(),
                     'FunFormKit.Form.FormServlet that renders (and caches) Grimoire method parameter forms')

    class funformkit(Grimoire.Performer.Method):
        def _call(performer):
            FormServlet = performer._callWithUnlockedTree(lambda: performer._getpath().formservlet())
            
            class SessionFormServlet(FormServlet):
                def getParams(self, method):
                    return self.grimoireSession().__._getpath(
                        path=['introspection', 'params'] + list(method)
                        )()

                def getFn(self, method):
                    return self.grimoireSession().__._getpath(path=list(method))

                def getComposer(self, *arg, **kw):
                    return self.grimoireSession().getComposer(*arg, **kw) 

                def handleCall(self, method, data):
                    result = FormServlet.handleCall(self, method, data)
                    if result.error is None:
                        sess = self.grimoireSession()
                        result.result = sess.handleResult(method, result.result)
                    return result

                def extraTrees(self):
                    directory = performer._getpath(Grimoire.Types.TreeRoot).directory.new()
                    directory.directory.set.parameters(['clients', 'html', 'webware', 'session'], self)
                    return [Grimoire._.trees.local.load(__name__ + '._performers'),
                            directory]

                def connectGrimoire(self, extraTrees = [], **kw):
                    sess = performer._callWithUnlockedTree(
                        lambda: performer._getpath(Grimoire.Types.MethodBase)()
                        )(extraTrees = extraTrees + self.extraTrees(), **kw)
                    sess.addView(())
                    self.session().setValue('GrimoireSession', Grimoire.Types.getValue(sess))
                    return sess

                def disconnectGrimoire(self):
                    s = self.session()
                    if s.hasValue('GrimoireSession'):
                        s.delValue('GrimoireSession')

                def reconnectGrimoire(self):
                    self.disconnectGrimoire()
                    return self.connectGrimoire()

                def isconnectedGrimoire(self):
                    return self.session().hasValue('GrimoireSession')

                def grimoireSession(self):
                    if not self.isconnectedGrimoire():
                        raise NameError
                    return self.session().value('GrimoireSession')

            return SessionFormServlet

        _call = Grimoire.Utils.cachingFunction(_call)
        def _params(self):
            return A(Ps(),
                     'FormServlet is a FunFormKit FormServlet wrapper for a ClientSession')
