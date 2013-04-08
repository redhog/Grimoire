from Grimoire.Utils.Types import Iter
import types, os, sys, string

debugExceptions = 0
raiseExceptions = 0

def allClasses(*modules):
    res = []
    for module in modules:
        res += filter(lambda x: type(x) == types.ClassType, module.__dict__.itervalues())
    return res

def modnamejoin(name1, name2):
    if name1:
        return name1 + '.' + name2
    else:
        return name2

def loadModule(name, raiseexception=True):
    components = string.split(name, '.')
    mod = None
    for prefix in Iter.Prefixes(components):
        name = string.join(prefix, '.')
        try:
            mod = __import__(name)
            break
        except [Exception, None][raiseexception]:
            pass
    if mod is None:
        raise NameError("Module does not exist:", name)
    for comp in components[1:]:
        if not hasattr(mod, comp):
            setattr(mod, comp, types.ModuleType(mod.__name__ + '.' + comp))
        mod = getattr(mod, comp)
    return mod

class ModuleTree:
    def __init__(self, modName, raiseexception=raiseExceptions):
        self.subModules = {}
        if raiseexception:
            self.module = loadModule(modName, True)
        else:
            try:
                self.module = loadModule(modName)
            except:
                import traceback
                if debugExceptions: traceback.print_exc()
                self.error = sys.exc_value
                self.trace = traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback)
                self.module = loadModule(modName, 0)                
        if hasattr(self.module, '__path__'):
            for path in self.module.__path__:
                for fileName in os.listdir(path):
                    if fileName.startswith('_') \
                       or fileName.startswith('.') \
                       or fileName.startswith('#'):
                        continue
                    if fileName.endswith('.py'):
                        subModName = fileName[:-3]
                        self.subModules[subModName] = ModuleTree(modName + '.' + subModName)
                    else:
                        filePath = os.path.join(path, fileName)
                        if os.path.isdir(filePath) \
                               and os.access(os.path.join(filePath,
                                                          '__init__.py'),
                                             os.F_OK):
                            self.subModules[fileName] = ModuleTree(modName + '.' + fileName)
