import types, re, string, Grimoire.Utils, Composable, Representation, Path, About, Introspection, urllib, xml.sax.saxutils


class ComposeType(object):
    class __metaclass__(types.TypeType):
        def __new__(cls, name, bases, members):
            for member in members:
                if isinstance(members[member], types.FunctionType):
                    members[member] = classmethod(members[member])
            return types.TypeType.__new__(cls, name, bases, members)
        def __call__(cls, *arg, **kw):
            return cls.compose(*arg, **kw)

    type = None

    def compose(cls, obj, composer):
        return obj

class Composer(object):

    translationTable = None
    currentMethod = None
    
    class __metaclass__(types.TypeType):
        def __new__(cls, name, bases, members):
            composeMap = Grimoire.Utils.InstanceMap()
            for base in bases:
                if hasattr(base, 'composeMap'):
                    composeMap.update(base.composeMap)
            for member in members.itervalues():
                if Grimoire.Utils.isSubclass(member, ComposeType) and member.type is not None:
                    composeMap[member.type] = member
            members['composeMap'] = composeMap
            return types.TypeType.__new__(cls, name, bases, members)

        def composeMapGet(composer, obj):
            return composer.composeMap[obj]
        composeMapGet = Grimoire.Utils.cachingFunction(composeMapGet)

        def __call__(composer, obj):
            return composer.composeMapGet(obj)(composer, obj)

    class ComposeString(ComposeType):
        type = types.BaseStringType

        def compose(cls, composer, obj):
            if hasattr(composer, 'translationTable') and composer.translationTable is not None:
                try:
                    return composer.translationTable(obj)
                except Grimoire.Utils.UntranslatableError:
                    pass
            return obj

    class ComposeException(ComposeType):
        type = Exception

        def compose(cls, composer, obj):
            if len(obj.args) == 1:
                return composer(obj.args[0])
            return composer(obj.args)

    class ComposeGrimoireReference(ComposeType):
        type = Representation.GrimoireReference

        def compose(cls, composer, obj):
            if composer.currentMethod is None:
                raise TypeError("Unable to render GrimoireReferences outside of method context")
            base = composer.currentMethod
            if obj['levels']:
                base = base[:-obj['levels']]
            return composer(Representation.GrimoirePath(base + obj['path']))

class TextComposer(Composer):
    class ComposePythonObject(ComposeType):
        type = Grimoire.Utils.AnyDescendant
        def compose(cls, composer, obj):
            try:
                # __unicode__ is not a classmethod, and if obj is a
                # class, we can't really do unicode(obj) or
                # obj.__unicode__() Python sucks.
                return type(obj).__unicode__(obj)
            except:
                pass
            try:
                return unicode(obj)
            except:
                pass
            try:
                return type(obj).__str__(obj)
            except:
                pass
            return str(obj)

    class ComposeObject(ComposeType):
        type = Composable.Composable
        def compose(cls, composer, obj):
            return '<' + composer(type(obj)) + ' at ' + str(id(obj)) + '>'

    class ComposeGenericMapping(ComposeType):
        type = None

        format = ''
        
        def getFormat(cls, composer, obj): return cls.format
        def getParams(cls, composer, obj): return obj

        __modre = re.compile('%\\(([^)]*)\\)([0-9.]*)s')
        def compose(cls, composer, obj):
            kw = {}
            for key, value in cls.getParams(composer, obj).iteritems():
                kw[key] = value
                kw['_unicode__' + key] = composer(kw[key])
            fmt = re.sub(cls.__modre, '%(_unicode__\\1)\\2s', composer(cls.getFormat(composer, obj)))
            return fmt % kw
   
    class ComposeFormattable(ComposeGenericMapping):
        type = Composable.Formattable
        def getFormat(self, composer, obj): return obj.format

    class ComposeSequence(ComposeType):
        type = None

        prefix = suffix = delimiter = ''
        
        def getPrefix(cls, composer, obj): return cls.prefix
        def getDelimiter(cls, composer, obj): return cls.delimiter
        def getSuffix(cls, composer, obj): return cls.suffix
        def getList(cls, composer, obj): return obj

        def compose(cls, composer, obj):
            return (  cls.getPrefix(composer, obj)
                    + string.join([composer(child) for child in cls.getList(composer, obj)],
                                  composer(cls.getDelimiter(composer, obj)))
                    + cls.getSuffix(composer, obj))

    class ComposeRepresentationSequence(ComposeSequence):
        type = Representation.RepresentationSequence
        def getDelimiter(cls, composer, obj): return obj.delimiter

    class ComposeReverseSequence(ComposeSequence):
        type = None

        def getReverseList(cls, composer, obj): return obj

        def getList(cls, composer, obj):
            return Grimoire.Utils.Reverse(cls.getReverseList(composer, obj))

    class ComposeRepresentationReverseSequence(ComposeRepresentationSequence, ComposeReverseSequence):
        type = Representation.RepresentationReverseSequence

    class ComposeList(ComposeSequence):
        type = types.ListType
        prefix = '['
        delimiter = ','
        suffix = ']'

    class ComposeTuple(ComposeList):
        type = types.TupleType
        prefix = '('
        suffix = ')'

    class ComposeReducible(ComposeSequence):
        type = Composable.Reducible
        def getDelimiter(cls, composer, obj): return obj.getDelimiter()

    class ComposeBlock(ComposeSequence):
        type = Composable.Block

    class ComposeLines(ComposeSequence):
        type = Composable.Lines
        delimiter = '\n'

    class ComposeParagraphs(ComposeSequence):
        type = Composable.Paragraphs
        delimiter = '\n\n'

    class ComposeAnnotatedValue(ComposeGenericMapping):
        type = Composable.AnnotatedValue
        def getFormat(cls, composer, obj):
            if obj['value'] is None:
                return '%(comment)s'
            return '%(comment)s: %(value)s'

    class ComposeGrimoirePath(ComposeRepresentationSequence):
        type = Representation.GrimoirePath

    class ComposeDN(ComposeRepresentationReverseSequence):
        type = Representation.DN

    class ComposeDNSDomain(ComposeRepresentationReverseSequence):
        type = Representation.DNSDomain
        
    class ComposeEMailAddress(ComposeGenericMapping):
        type = Representation.EMailAddress
        format = '%(username)s@%(domain)s'

    class ComposePathCombination(ComposeSequence):
        type = Path.PathCombination
        def getList(cls, composer, obj):
            res = []
            if 'header' in obj: res.append(obj['header'])
            if 'relative' in obj: res.append(obj['relative'])
            if 'trailer' in obj: res.append(obj['trailer'])
            return res

    class ComposeURIHeader(ComposeGenericMapping):
        type = Path.URIHeader
        def getFormat(cls, composer, obj):
            format = ''
            if 'method' in obj:
                format += '%(method)s://'
                if 'source' in obj:
                    if 'user' in obj:
                        format += '%(user)s'
                        if 'pwd' in obj:
                            format += ':%(pwd)s'
                        format += '@'
                    format += '%(source)s'
                    if 'port' in obj:
                        format += ':%(port)s'
            format += '/'
            return format
        
    class ComposeURIParameters(ComposeType):
        type = Path.URIParameters

        def compose(cls, composer, obj):
            if not obj:
                return ''
            return '?' + '&'.join([key + '=' + obj[key] for key in obj])

    class ComposeLocalHeader(ComposeGenericMapping):
        type = Path.LocalHeader
        def getFormat(cls, composer, obj):
            if obj['method'] == 'unc':
                return '//%(source)s'
            return '%(source)s'

    class ComposeCopyrightChange(ComposeGenericMapping):
        type = About.CopyrightChange
        format = '%(type)s (c) %(year)s by %(name)s <%(email)s>'

    class ComposeAboutItem(ComposeGenericMapping):
        type = About.AboutItem
        format = """%(name)s
Version: %(versionname)s
%(copychanges)s
License: %(licenseURL)s

%(licenseText)s"""
        def getParams(cls, composer, obj):
            res = {}
            res.update(obj)
            res['copychanges'] = Composable.Lines(res['copyright'], *res['changes'])
            return res

    class ComposeParamsType(ComposeType):
        type = Introspection.ParamsType
        def compose(cls, composer, obj):
            lines = []
            if obj.arglist:
                if obj.required:
                    lines.append(Grimoire.Types.AnnotatedValue(
                        Grimoire.Types.Lines(*[Grimoire.Types.AnnotatedValue(type, name) for (name, type) in obj.arglist[:obj.required]]),
                        "Required arguments"))
                else:
                    lines.append("No required arguments.")
                if obj.required < len(obj.arglist):
                    lines.append(Grimoire.Types.AnnotatedValue(
                        Grimoire.Types.Lines(*[Grimoire.Types.AnnotatedValue(type, name) for (name, type) in obj.arglist[obj.required:]]),
                        "Optional arguments"))
                else:
                    lines.append("No optional arguments.")
            if obj.resargstype:
                lines.append(Grimoire.Types.AnnotatedValue(obj.resargstype, "Type for extra arguments"))
            else:
                lines.append("No extra arguments allowed.")
            if obj.reskwtype:
                lines.append(Grimoire.Types.AnnotatedValue(obj.resargstype, "Type for extra keyword arguments"))
            else:
                lines.append("No extra keyword arguments allowed.")
            if obj.convertType:
                lines.append(Grimoire.Types.AnnotatedValue(obj.convertType, "Values will be converted to the following types"))
            return composer(Grimoire.Types.Lines(*lines))

class HtmlNoEscape(types.UnicodeType): pass
class HtmlParagraph(types.DictType): pass

class HtmlComposer(TextComposer):

    methodBaseURI = None # URI pattern for GrimoireReference expansion. Example: "http://example.com/grimoire?sess=4711&callMethod=%(method)s&foo=32"

    class ComposePythonObject(TextComposer.ComposePythonObject):
        def compose(cls, composer, obj):
            return xml.sax.saxutils.escape(TextComposer.ComposePythonObject.compose(composer, obj))

    class ComposeObject(TextComposer.ComposeObject):
        def compose(cls, composer, obj):
            return '&lt;' + composer(type(obj)) + ' at ' + str(id(obj)) + '&gt;'

    class ComposeHtmlNoEscape(TextComposer.ComposeString):
        type = HtmlNoEscape

    class ComposeString(TextComposer.ComposeString):
        def compose(cls, composer, obj):
            return xml.sax.saxutils.escape(TextComposer.ComposeString.compose(composer, obj))

    class ComposeLines(TextComposer.ComposeLines):
        def getDelimiter(cls, composer, obj): return HtmlNoEscape('<br/>')

    class ComposeParagraph(TextComposer.ComposeGenericMapping):
        type = HtmlParagraph
        format = HtmlNoEscape('<p>%(paragraph)s</p>')

    class ComposeParagraphs(TextComposer.ComposeParagraphs):
        type = Composable.Paragraphs
        def getList(cls, composer, obj):
            return [HtmlParagraph(paragraph=paragraph)
                    for paragraph in TextComposer.ComposeBlock.getList(composer, obj)]

    class ComposeTitledURILink(TextComposer.ComposeGenericMapping):
        type = Composable.TitledURILink
        format = HtmlNoEscape('<a href="%(value)s">%(comment)s</a>')

    class ComposeGrimoireReference(TextComposer.ComposeGrimoireReference):
        def compose(cls, composer, obj):
            if composer.methodBaseURI is None:
                raise TypeError("Unable to render GrimoirePaths without a medthod base URI")
            return composer.methodBaseURI % {
                'method': urllib.quote_plus(Grimoire.Utils.encode(
                    "." +  TextComposer.ComposeGrimoireReference.compose(composer, obj)))}

    class ComposeCopyrightChange(TextComposer.ComposeCopyrightChange):
        format = HtmlNoEscape('%(type)s (c) %(year)s by %(name)s &lt;<a href="mailto:%(email)s">%(email)s</a>&gt;')

    class ComposeAboutItem(TextComposer.ComposeAboutItem):
        format = HtmlNoEscape("""%(name)s<br/>
<p>
 Version: %(versionname)s<br/>
 %(copychanges)s<br/>
 License: %(licenseURL)s
</p>
%(licenseText)s""")