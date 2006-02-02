import string, re, types, UserString, Grimoire.Utils, Grimoire.Utils.Serialize.Reader
import Composable

debugTypes = False


AnyType = object
    
class LosePasswordType(types.StringType): pass
class LoseNewPasswordType(LosePasswordType): pass

usernameTypeRegexp = re.compile('^[' + string.ascii_letters + '][' + string.ascii_letters + string.digits + ']*$')
class UsernameType(types.StringType):
    def __init__(self, value):
        if not usernameTypeRegexp.search(value):
            raise Exception('Usernames must be all letters (a-z) and digits, and begin with a letter')
        super(UsernameType, self).__init__(value)

# Backward combatability
BooleanType = types.BooleanType

class SerialType(types.IntType): pass


class ExtendWithDefaults: pass
def extendTupleWithDefaults(preDefaults = (), tuple = None, postDefaults = ()):
    if tuple is None:
        tuple = (ExtendWithDefaults,)
    if ExtendWithDefaults in tuple:
        tuple = preDefaults + tuple + postDefaults
    return tuple
def extendDictWithDefaults(dict = None, defaults = {}):
    if dict is None:
        dict = {ExtendWithDefaults:ExtendWithDefaults}
    if ExtendWithDefaults in dict:
        d = {}
        d.update(defaults)
        d.update(dict)
        dict = d
    return dict

def getDefAttr(bases, dict, name):
    if dict and name in dict:
            return dict[name]
    if bases:
        for base in bases:
            try:
                return getattr(base, name)
            except Exception:
                pass
    raise AttributeError(name)

def hasDefAttr(bases, dict, name):
    try:
        getDefAttr(bases, dict, name)
        return True
    except AttributeError:
        return False

class GeneratedType(types.TypeType):
    description = 'generated'
    specializedTypes = {}
    def __new__(cls, name, bases = (), dict = None):
        tag = cls.getTag(name, bases, dict)
        if debugTypes: print tag, ' --> ', cls, name, bases, dict
        if tag not in cls.specializedTypes:
            d = extendDictWithDefaults(dict, {'__metaclass__':cls})
            if ExtendWithDefaults in d: del d[ExtendWithDefaults]
            if ExtendWithDefaults in bases:
                bases = list(bases)
                bases.remove(ExtendWithDefaults)
                bases = tuple(bases)
            if '__metaclass__' in d:
                cls = d['__metaclass__']            
            newcls = Grimoire.Utils.mergeClasses([cls] + [type(base) for base in bases])
            if newcls is not cls:
                d['__metaclass__'] = cls = newcls
            cls.specializedTypes[tag] = types.TypeType.__new__(cls, name, bases, d)
            cls.specializedTypes[tag].tag = tag
        return cls.specializedTypes[tag]
    def getTag(cls, name, bases = (), dict = {}, tag = ()):
        if 'tag' in dict:
            return dict['tag']
        else:
            prefix = (cls.description,)
            try:
                prefix += (getDefAttr(bases, dict, 'description'),)
            except AttributeError:
                prefix += (name,)
            return prefix + tag
    getTag = classmethod(getTag)
    def __unicode__(self):
        return string.join([unicode(obj) for obj in self.tag], ' ')
    def __str__(self):
        return unicode(self).encode()
class GenericGeneratedType(object):
    __metaclass__ = GeneratedType
GeneratedType.generic = GenericGeneratedType

class StaticDerivedType(GeneratedType):
    description = 'derived from'
    def __new__(cls, name = None, bases = None, dict = None):
        return super(StaticDerivedType, cls).__new__(
            cls, name or cls.__name__, extendTupleWithDefaults((cls.generic,), bases, ()), dict)
    def getTag(cls, name, bases = (), dict = {}, tag = ()):
        if len(tag) > 1:
            return (tag[0], cls.description) + tag[1:]
        else:
            return (cls.description,) + tag
    getTag = classmethod(getTag)
    def derive(cls, name = None, bases = None, dict = None):
        return cls(name, bases, dict)
    derive = classmethod(derive)
    def __isInstance__(self, obj):
        return Grimoire.Utils.isInstance(obj, self.parentType)
class GenericStaticDerivedType(GenericGeneratedType):
    __metaclass__ = StaticDerivedType
    parentType = AnyType
StaticDerivedType.generic = GenericStaticDerivedType

class DerivedType(StaticDerivedType):
    # FIXME: Use EMRO to getDefAttr(bases, dict, 'parentType') from generic too!
    def __new__(cls, name = None, bases = None, dict = None):
        b = bases
        try:
            b = extendTupleWithDefaults((), bases, (getDefAttr(bases, dict, 'parentType'),))
        except AttributeError:
            pass
        return super(DerivedType, cls).__new__(cls, name, b, dict)
    def derive(cls, parentType = None, name = None, bases = None, dict = None):
        d = dict
        if parentType is not None:
            d = extendDictWithDefaults(d, {'parentType':parentType})
        return super(DerivedType, cls).derive(name, bases, d)
    derive = classmethod(derive)
    def getTag(cls, name, bases = (), dict = {}, tag = ()):
        return super(DerivedType, cls).getTag(name, bases, dict, (getDefAttr(bases, dict, 'parentType'),) + tag)
    getTag = classmethod(getTag)
class GenericDerivedType(GenericStaticDerivedType):
    __metaclass__ = DerivedType
DerivedType.generic = GenericDerivedType

class NonemptyType(DerivedType):
    description = 'nonempty'
    def __isInstance__(self, obj):
        return obj and super(NonemptyType, self).__isInstance__(obj)
class GenericNonemptyType(GenericDerivedType):
    __metaclass__ = NonemptyType
    def __init__(self, value):
        if not value:
            raise ValueError('Empty value')
        super(GenericNonemptyType, self).__init__(self.parentType(value))
NonemptyType.generic = GenericNonemptyType

PasswordType = NonemptyType.derive(LosePasswordType)
NewPasswordType = NonemptyType.derive(LoseNewPasswordType)
NonemptyStringType = NonemptyType.derive(types.StringType)
NonemptyUnicodeType = NonemptyType.derive(types.UnicodeType)

class ContainerType(StaticDerivedType):
    description = 'container for'
    def derive(cls, containedType = None, name = None, bases = None, dict = None):
        d = dict
        if containedType is not None:
            d = extendDictWithDefaults(d, {'containedType':containedType})
        return super(ContainerType, cls).derive(name, bases, d)
    derive = classmethod(derive)
    def getTag(cls, name, bases = (), dict = {}, tag = ()):
        return super(ContainerType, cls).getTag(name, bases, dict, (getDefAttr(bases, dict, 'containedType'),) + tag)
    getTag = classmethod(getTag)
class GenericContainerType(GenericStaticDerivedType):
    __metaclass__ = ContainerType
    containedType = AnyType
ContainerType.generic = GenericContainerType

class ListType(ContainerType):
    description = 'list of'
    def __isInstance__(self, obj):
        return (    super(ListType, self).__isInstance__(obj)
                and reduce(
                    lambda res, item: res and Grimoire.Utils.isInstance(item, self.containedType),
                    obj, True))
class GenericListType(GenericContainerType, types.ListType):
    __metaclass__ = ListType
    parentType = types.ListType
    def __init__(self, value):
        if Grimoire.Utils.isInstance(value, types.BaseStringType):
            value = Grimoire.Utils.Serialize.Reader.read(Grimoire.Utils.Serialize.Reader.Buffer(value))
        super(GenericListType, self).__init__(map(self.containedType, value))
    def __setitem__(self, index, value):
        if Grimoire.Utils.isInstance(index, types.SliceType):
            value = map(self.containedType, value)
        else:
            value = self.containedType(value)
        super(GenericListType, self).__setitem__(index, value)
ListType.generic = GenericListType

StringListType = ListType.derive(types.StringType)
UnicodeListType = ListType.derive(types.UnicodeType)

class EncodedStringType(StaticDerivedType):
    description = "string with contents encoded in"
    def derive(cls, encoding = None, name = None, bases = None, dict = None):
        d = dict
        if encoding is not None:
            d = extendDictWithDefaults(d, {'encoding':encoding})
        return super(EncodedStringType, cls).derive(name, bases, d)
    derive = classmethod(derive)
    def getTag(cls, name, bases = (), dict = {}, tag = ()):
        return super(EncodedStringType, cls).getTag(name, bases, dict, (getDefAttr(bases, dict, 'encoding'),) + tag)
    getTag = classmethod(getTag)
    def __isInstance__(self, value):
        try:
            value.decode(self.encoding)
            return 1
        except Exception:
            return 0
class GenericEncodedStringType(GenericDerivedType, types.StringType):
    __metaclass__ = EncodedStringType
    parentType = types.StringType
    encoding = 'utf-8'
    def __init__(self, value):
        super(GenericEncodedStringType, self).__init__(
            Grimoire.Utils.encode(
                value,
                self.encoding))
    def __unicode__(self):
        return self.decode(self.encoding)
EncodedStringType.generic = GenericEncodedStringType

UTF8Type = EncodedStringType.derive('utf-8')

class ValuedType(DerivedType):
    def derive(cls, parentType = None, values = (), name = None, bases = None, dict = None):
        d = extendDictWithDefaults(dict, {'values':tuple(values)})
        return super(ValuedType, cls).derive(parentType, name, bases, d)
    derive = classmethod(derive)
    def getTag(cls, name, bases = (), dict = {}, tag = ()):
        return super(ValuedType, cls).getTag(name, bases, dict, (getDefAttr(bases, dict, 'values'),) + tag)
    getTag = classmethod(getTag)
    def getValues(self):
        return self.values
    def __strValues__(self):
        values = [unicode(value) for value in self.getValues()]
        if len(values) > 1:
            values[-1] = 'or ' + values[-1]
        return string.join(values, ', ')
class GenericValuedType(GenericDerivedType):
    __metaclass__ = ValuedType
    values = ()
    def __init__(self, value):
        super(GenericValuedType, self).__init__(self.parentType(value))
ValuedType.generic = GenericValuedType

class HintedType(ValuedType):
    description = 'with suggested values'
    def __unicode__(self):
        values = self.__strValues__()
        res = unicode(self.parentType)
        if values:
            res += ' with suggested values ' + values
        return res
class GenericHintedType(GenericValuedType):
    __metaclass__ = HintedType
HintedType.generic = GenericHintedType

class RestrictedType(ValuedType):
    description = "any of"
    def __isInstance__(self, value):
        bareValues = map(Composable.getValue, self.getValues())
        return (    super(RestrictedType, self).__isInstance__(value)
                and self.parentType(value) in bareValues)

    def __unicode__(self):
        if self.getValues():
            return 'any of %(values)s (of type %(parentType)s)' % {
                'values': self.__strValues__(),
                'parentType': unicode(self.parentType)}
        else:
            return 'No allowed values! (of type %(parentType)s)' % {
                'parentType': unicode(self.parentType)}
class GenericRestrictedType(GenericValuedType):
    __metaclass__ = RestrictedType
    def __init__(self, value):
        value = self.parentType(value)
        super(GenericRestrictedType, self).__init__(value)
        bareValues = map(Composable.getValue, self.__class__.getValues())
        if value not in bareValues:
            raise ValueError('Value %(value)s not from list of available/possible values %(lst)s' % {
                'value': repr(value),
                'lst': repr(bareValues)})
RestrictedType.generic = GenericRestrictedType

class BitfieldType(ValuedType):
    description = "Bitfield"
class GenericBitfieldType(GenericValuedType):
    __metaclass__ = BitfieldType
    def __init__(self, value):
        value = value or 0
        if hasattr(value, '__getitem__'):
            value = reduce(lambda x, y: x | y,
                           [self.parentType(v) for v in value])
        super(GenericBitfieldType, self).__init__(self.parentType(value))
BitfieldType.generic = GenericBitfieldType

pathSeparator = ' '
