from distutils.core import *
setup(name = "Grimoire", version = "0.1",
      ext_modules = [Extension("Utils.Serialize.CReader", ["Utils/Serialize/CReader.c"])])
