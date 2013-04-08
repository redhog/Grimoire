import types, weakref

if not hasattr(types, 'BaseStringType'):
    types.BaseStringType = types.StringType.__bases__[0]

if not hasattr(types, 'GetsetDescriptor'):
    class Tmp(types.StringType): pass
    types.GetsetDescriptor = type(Tmp.__dict__['__dict__'])

if not hasattr(types, 'MethodWrapper'):
    class Tmp(types.StringType): pass
    types.MethodWrapper = Tmp.__dict__['__dict__'].__get__.__class__

if not hasattr(types, 'ReferenceType'):
    types.ReferenceType = weakref.ReferenceType

import Socket

from Grimoire.Utils.Types.Inf import *
from Grimoire.Utils.Types.Iter import *
from Grimoire.Utils.Types.Maps import *
from Grimoire.Utils.Types.SortedList import *
from Grimoire.Utils.Types.Thread import *
from Grimoire.Utils.Types.Wrapper import *
from Grimoire.Utils.Types.EMRO import *
from Grimoire.Utils.Types.Gettext import *
from Grimoire.Utils.Encode import *
from Grimoire.Utils.Fn import *
from Grimoire.Utils.List import *
from Grimoire.Utils.MixIn import *
from Grimoire.Utils.Module import *
from Grimoire.Utils.Obj import *
from Grimoire.Utils.Process import *
from Grimoire.Utils.Filesystem import *
