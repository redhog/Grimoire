# Classes allowed to desrialize. As classes can do pretty much
# anything when instanciated, and even when created (as they are only
# instances of their meta-classes, which can do anything at
# instanciation time), allowing deserialization of any and every class
# is a huge security hole. The set of allowed classes should be kept
# as small as possible. You have been warned.
#
# A class is specified using a path of
# first the module of the class, then the name of the
# class. E.g. ['foo', 'bar', 'fie', 'naja'] means the class naja in
# the module foo.bar.fie (or the class fie.naja in the module foo.bar,
# or the class bar.fie.naja in the module foo). A list prefixed by '/'
# means to only allow the class if it is a subclass of another,
# allowed class.
#
# The default value is to only allow deserialization of classes within
# the exception, types, Grimoire.Types and Grimoire.About modules. You
# probably want the default for all sane situations.
#
# import Grimoire
# set([], Grimoire.Types.Ability.List([(Grimoire.Types.Ability.Deny, [])]))
