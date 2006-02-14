import Grimoire.Performer, Grimoire.Utils, Grimoire.Utils.Gettext, Grimoire.Types, os, os.path, imp, string, sys, types, traceback

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive


debugExceptions = 0
raiseExceptions = 0

class ErrorDialog(Grimoire.Performer.SubMethod):
    def __init__(self, type, error, trace):
        Grimoire.Performer.SubMethod.__init__(self)
        self._type = type
        self._error = error
        self._trace = trace
    def _call(self, path, *arg, **kw):
        raise Exception(
            Grimoire.Types.Lines(
                Grimoire.Types.Formattable('An error occured while %(when)s: %(error)s',
                                           when = ['loading the file',
                                                   'instanciating the Performer class'][self._type],
                                           error = self._error),
                *self._trace))
    def _dir(self, path, depth):
        return [(1, []), (1, ['error'])]
    def _params(self, path):
        return Grimoire.Types.ParamsType.derive()

# FIXME: Include translations of domains that are not Performers, too


class Performer(Grimoire.Performer.Base):
    class load(Grimoire.Performer.Method):
        def _call(self, modName, raiseexception=raiseExceptions):
            def translationsOfModule(module):
                if not hasattr(module, '__file__'):
                    return None
                path, file = os.path.split(module.__file__)
                file = file.split('.', 1)[0]
                if file == '__init__':
                    path, file = os.path.split(path)
                return Grimoire.Utils.Gettext.Translations(os.path.join(path, '_Translations'), file, None)

            def moduleTree2PerformerList(res, pathPrefix, modTree):
                addprefix = pathPrefix[:-1]
                translations = translationsOfModule(modTree.module)
                if translations:
                    translations = Grimoire.Performer.Translation(translations)
                    if addprefix:
                        translations = Grimoire.Performer.Prefixer(addprefix, translations)
                    res.append(translations)
                try:
                    if pathPrefix:
                        performer = None
                        if hasattr(modTree, 'error'):
                            type = 0
                            error = modTree.error
                            trace = modTree.trace
                        else:
                            performerClass = modTree.module.Performer
                            try:
                                performer = performerClass()
                            except:
                                if debugExceptions: traceback.print_exc()
                                if raiseexception:
                                    raise sys.exc_type, sys.exc_value, sys.exc_traceback
                                type = 1
                                error = sys.exc_value
                                trace = traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback)
                        if performer is None:
                            addprefix = pathPrefix
                            performer = ErrorDialog(type, error, trace)
                        if addprefix:
                            performer = Grimoire.Performer.Prefixer(addprefix, performer)
                        res.append(performer)
                except AttributeError:
                    pass
                for subModTreeeName, subModTreee in modTree.subModules.iteritems():
                    moduleTree2PerformerList(res, pathPrefix + [subModTreeeName], subModTreee)
            res = []
            moduleTree2PerformerList(res, [], Grimoire.Utils.ModuleTree(modName, raiseexception))
            return Grimoire.Performer.Composer(*res)
        def _params(self):
            return A(Ps([('modName', A(types.StringType, 'Module path to root Python module of the Grimoire tree')),
                         ('raiseexception', A(types.BooleanType, 'Wether to raise exceptions during load'))],
                        1),
                     'Load a tree of python modules and .po-files, defining a Grimoire tree including its tanslations. modName should be a string reffering to the topp-level module to be loaded and used in this way, e.g. "foo.bar.mymodule". Please see "Loading trees" in the file "Documentation/Overview.html" for information on the directory-structure needed for the module-files.')

    class load_standardtree(Grimoire.Performer.Method):
        def _call(self, modName,
                  initcommandspath = ['parameters'], initcommandskeypath = ['initcommands'],
                  ability = None,
                  directory = None,
                  raiseexception = raiseExceptions,
                  extra = None):
            
            dir = directory or self._callWithUnlockedTree(lambda: self._getpath(Grimoire.Types.TreeRoot).directory.new())
            
            tree = Grimoire.Performer.Composer(
                Grimoire.Performer.Prefixer(
                    ['introspection'],
                    self._callWithUnlockedTree(lambda: self._getpath(Grimoire.Types.TreeRoot).trees.introspection())),
                dir,
                self._callWithUnlockedTree(lambda: self._getpath(levels=1)(modName, raiseexception)),
                Grimoire.Performer.Isolator(extra or self._getpath(Grimoire.Types.TreeRoot)))

            if ability is not None:
                tree = Grimoire.Performer.Restrictor(tree, ability)

            if initcommandspath and initcommandskeypath:
                exprs = Grimoire.Utils.Flatten(
                    Grimoire.Utils.Reverse(
                        tree._callWithUnlockedTree(
                            lambda: tree._getpath(path=['directory', 'get'] + initcommandspath
                                                  )(initcommandskeypath, all = True))))
                errors = []
                for expr in exprs:
                    try:
                        Grimoire.Performer.Logical(tree).introspection.eval(expr)
                    except Exception, e:
                        e.trace = traceback.extract_tb(sys.exc_info()[2])
                        errors.append(e)
                if errors:
                    tree = A(tree, Grimoire.Types.Lines(*errors))
            return tree
        def _params(self):
            return A(Ps([('modName', A(types.StringType, 'Module path to root Python module of the Grimoire tree')),
                         ('initcommandspath', A(Grimoire.Types.UnicodeListType, '')),
                         ('initcommandskeypath', A(Grimoire.Types.UnicodeListType, '')),
                         ('raiseexception', A(types.BooleanType, 'Wether to raise exceptions during load'))],
                        1),
                     'As trees.local.load, but adds introspection, mirroring of the main tree, execution of initcommands and addition of any extra trees (such as directory)')

        
