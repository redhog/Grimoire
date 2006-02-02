import Grimoire.Performer, Grimoire.Utils, Grimoire.Types, Grimoire.Types.Ability, os


comp = Grimoire.Performer.Composer
pref = Grimoire.Performer.Prefixer
iso = Grimoire.Performer.Isolator
Physical = Grimoire.Performer.Physical
Logical = Grimoire.Performer.Logical

# Serious boot-strapping
import Grimoire.root.trees.local.load

__ = Logical(Grimoire.root.trees.local.load.Performer()).load('Grimoire.root')
_ = Logical(__)
__._insert(pref(['introspection'], _.trees.introspection()), True)

serverTreesAbility = Grimoire.Types.Ability.List(
    [(Grimoire.Types.Ability.Allow, ['introspection']),
     (Grimoire.Types.Ability.Deny, ['trees', 'local', 'unprotected']),
     (Grimoire.Types.Ability.Allow, ['trees', 'local']),
     ])

noIntrospectionAbility = Grimoire.Types.Ability.List(
    [(Grimoire.Types.Ability.Deny, ['introspection']),
     (Grimoire.Types.Ability.Allow, []),
     ])

serverTrees = Grimoire.Performer.Restrictor(
    comp(pref(['introspection'], _.trees.introspection()),
         iso(_)),
    serverTreesAbility)


cfgDirs = [Grimoire.Types.defaultLocalRoot + ['etc', 'Grimoire']]
if 'HOME' in os.environ:
    cfgDirs += [Grimoire.Types.LocalPath(os.environ['HOME']) + ['.Grimoire']]
if 'CHOICES' in os.environ:
    cfgDirs += [Grimoire.Types.LocalPath(path) + ['Grimoire'] for path in os.environ['CHOICES'].split(':')]
_.directory.set.parameters(['directories'], cfgDirs)

cfgFiles = [path + ['Config.py'] for path in cfgDirs if os.access(unicode(path + ['Config.py']), os.F_OK)]
_.directory.set.parameters(['files'], cfgFiles)

cfgTrees = [path + ['Config.d'] for path in cfgDirs if os.access(unicode(path + ['Config.d']), os.F_OK)]
_.directory.set.parameters(['trees'], cfgTrees)


class Set(Grimoire.Performer.SubMethod):
    def _call(self, path, keyPath, *arg, **kw):
        __._getpath(path = list(['directory', 'set'] + configPath + path))(list(configKeyPath + keyPath), *arg, **kw)
    def _dir(self, path, depth):
        return __._getpath(path = ['introspection', 'dir', 'directory', 'set'] + configPath + path)(path, depth)
    def _params(self, path):
        return __._getpath(path = ['introspection', 'params', 'directory', 'set'] + configPath + path)(path)
set = Logical(Set())
class Get(Grimoire.Performer.SubMethod):
    def _call(self, path, keyPath, *arg, **kw):
        return __._getpath(path = ['directory', 'get'] + configPath + path)(configKeyPath + keyPath, *arg, **kw)
    def _dir(self, path, depth):
        return __._getpath(path = ['introspection', 'dir', 'directory', 'get'] + configPath + path)(path, depth)
    def _params(self, path):
        return __._getpath(path = ['introspection', 'params', 'directory', 'get'] + configPath + path)(path)
get = Logical(Get())

def treevar(varname, value):
    _.directory.set.treevar(['treevar', varname], value)


configPath = configKeyPath = []

for configFilePath in _.directory.get.parameters(['files']):
    try:
        execfile(unicode(configFilePath))
    except IOError:
        pass

for configTree in _.directory.get.parameters(['trees']):
    for dirpath, dirnames, filenames in os.walk(unicode(configTree)):
        for filename in filenames:
            configFilePath = Grimoire.Types.LocalPath(os.path.join(dirpath, filename))
            keyPath = configFilePath[len(configTree):]['relative']
            if keyPath[-1].endswith('.py'):
                keyPath[-1] = keyPath[-1][:-3] # Remove .py"
                configPath, configKeyPath = Grimoire.Utils.splitList(keyPath, '_settings', 2)
                try:
                    execfile(unicode(configFilePath))
                except IOError:
                    pass

configPath = configKeyPath = []
