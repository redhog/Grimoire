"""This module defines (string) objects that can be translated and
composed in different manners. It may be used to deffer composition
til a later time (e.g. until the data is on the client side of ome
connection), and to allow the objects to be composed in a manner
suitable for the composing software (e.g. with interleaving HTML-tags,
wrapped up in Gtk+ widgets, etc), and translated into a language
uitable for the user.
"""

import string, re, types, Grimoire.Utils, Composer

class Composable(object):
    def __unicode__(self):
        return Composer.TextComposer(self)
    def __str__(self):
        return str(unicode(self))

class Mapping(Grimoire.Utils.ImmutableMapping, Composable):
    def __cmp__(self, other):
        return cmp(type(self), type(other)) or super(Mapping, self).__cmp__(other)

class Formattable(Mapping):
    """Defines a string made up of several separate parts merged
    together using a format-string. The syntax of the format-string is
    as for the Python % operator when the right-hand-side is a
    mapping.
    """
    def __init__(self, format, **params):
        types.DictType.__init__(self, **params)
        self.format = format

    def getFormatParams(self):
        class CollectItems:
            def __init__(self): 
                self.items = []
            def __getitem__(self, name):
                self.items += [name]
                return name
        collectItems = CollectItems()
        self.format % collectItems
        return collectItems.items

class Sequence(types.ListType, Composable):
    def __eq__(self, other):
	return type(self) is type(other) and super(Sequence, self).__eq__(other)
    def __ne__(self, other):
	return type(self) != type(other) or super(Sequence, self).__ne__(other)
    def __ge__(self, other):
	return type(self) is type(other) and super(Sequence, self).__ge__(other)
    def __gt__(self, other):
	return type(self) is type(other) and super(Sequence, self).__gt__(other)
    def __le__(self, other):
	return type(self) is type(other) and super(Sequence, self).__le__(other)
    def __lt__(self, other):
	return type(self) is type(other) and super(Sequence, self).__lt__(other)
    def __cmp__(self, other):
        return cmp(type(self), type(other)) or super(Sequence, self).__cmp__(other)
    def __getslice__(self, *arg, **kw):
        return type(self)(super(Sequence, self).__getslice__(*arg, **kw))
    def __add__(self, *arg):
        try:
            return type(self)(super(Sequence, self).__add__(*arg))
        except TypeError, e:
            if len(arg) == 1 and hasattr(arg[0], "__radd__"):
                return arg[0].__radd__(self)
            raise e
    def __radd__(self, other): # ListType does not implement radd.
        return type(self)(other.__add__(self))
    def __mul__(self, *arg):
        return type(self)(super(Sequence, self).__mul__(*arg))

class Reducible(Sequence):
    """Defines a string made up of a list of several parts, joined
    with some delimiter.
    """
    def __init__(self, list, delimiter):
        types.ListType.__init__(self, list)
        self.delimiter = delimiter
    def getDelimiter(self):
        return self.delimiter

class EnumerateSequence(Sequence):
    """Base class for sequences that are instantiated like class(elem1, elem2, ... elemn), not class([elem1, elem2, ... elemn])."""
    def __init__(self, *arg):
        Sequence.__init__(self, arg)
    def __getslice__(self, *arg, **kw):
        return type(self)(*super(Sequence, self).__getslice__(*arg, **kw))
    def __add__(self, *arg, **kw):
        return type(self)(*super(Sequence, self).__add__(*arg, **kw))
    def __radd__(self, *arg, **kw):
        return type(self)(*super(Sequence, self).__radd__(*arg, **kw))
    def __mul__(self, *arg, **kw):
        return type(self)(*super(Sequence, self).__mul__(*arg, **kw))

class Block(EnumerateSequence):
    """Joins several composable objects with no interleaving space."""

class Lines(EnumerateSequence):
    """Joins several composable objects as separate lines (interleave
    newlines).
    """

class Paragraphs(EnumerateSequence):
    """Joins several composable objects as separate paragraphs.
    """

class AnnotatedValue(Mapping):
    def __init__(self, value, comment):
        Mapping.__init__(self, value=value, comment=comment)
    #### fixme ####
    # name = 'AnnotatedValue:mirror'
    # description = """Why do we let AnnotatedValues be similar to the value
    # within them anyway?? When is it needed?"""
    #### end ####
    def __isSubclassOf__(self, o): return False
    def __isSubclass__(self, o): return False
    def __instanceOf__(self): return type(self)
    def __isInstanceOf__(self, t): isinstance(self, t)
    def __isInstance__(self, o): isinstance(t, self)
    def __getattr__(self, name):
        return getattr(self['value'], name)

def getValue(value):
    if Grimoire.Utils.isInstance(value, AnnotatedValue):
        return value['value']
    return value

def getComment(value, comment = None):
    if Grimoire.Utils.isInstance(value, AnnotatedValue):
        return value['comment']
    return comment

class TitledURILink(AnnotatedValue): pass
