Import Grimoire.Types, types, xml.sax.saxutils, urllib

class HtmlNoEscape(types.UnicodeType): pass
class HtmlParagraph(types.DictType): pass

class HtmlComposer(Grimoire.Types.TextComposer):

    methodBaseURI = None # URI pattern for GrimoireReference expansion. Example: "http://example.com/grimoire?sess=4711&callMethod=%(method)s&foo=32"

    class ComposePythonObject(Grimoire.Types.TextComposer.ComposePythonObject):
        def compose(cls, composer, obj):
            return xml.sax.saxutils.escape(Grimoire.Types.TextComposer.ComposePythonObject.compose(composer, obj))

    class ComposeObject(Grimoire.Types.TextComposer.ComposeObject):
        def compose(cls, composer, obj):
            return '&lt;' + composer(type(obj)) + ' at ' + str(id(obj)) + '&gt;'

    class ComposeHtmlNoEscape(Grimoire.Types.TextComposer.ComposeString):
        type = HtmlNoEscape

    class ComposeString(Grimoire.Types.TextComposer.ComposeString):
        def compose(cls, composer, obj):
            return xml.sax.saxutils.escape(Grimoire.Types.TextComposer.ComposeString.compose(composer, obj))

    class ComposeLines(Grimoire.Types.TextComposer.ComposeLines):
        def getDelimiter(cls, composer, obj): return HtmlNoEscape('<br/>')

    class ComposeParagraph(Grimoire.Types.TextComposer.ComposeGenericMapping):
        type = HtmlParagraph
        format = HtmlNoEscape('<p>%(paragraph)s</p>')

    class ComposeParagraphs(Grimoire.Types.TextComposer.ComposeParagraphs):
        type = Composable.Paragraphs
        def getList(cls, composer, obj):
            return [HtmlParagraph(paragraph=paragraph)
                    for paragraph in Grimoire.Types.TextComposer.ComposeBlock.getList(composer, obj)]

    class ComposeTitledURILink(Grimoire.Types.TextComposer.ComposeGenericMapping):
        type = Composable.TitledURILink
        format = HtmlNoEscape('<a href="%(value)s">%(comment)s</a>')

    class ComposeGrimoireReference(Grimoire.Types.TextComposer.ComposeGrimoireReference):
        def compose(cls, composer, obj):
            if composer.methodBaseURI is None:
                raise TypeError("Unable to render GrimoirePaths without a medthod base URI")
            return composer.methodBaseURI % {
                'method': urllib.quote_plus(Grimoire.Utils.encode(
                    "." +  Grimoire.Types.TextComposer.ComposeGrimoireReference.compose(composer, obj)))}

    class ComposeCopyrightChange(Grimoire.Types.TextComposer.ComposeCopyrightChange):
        format = HtmlNoEscape('%(type)s (c) %(year)s by %(name)s &lt;<a href="mailto:%(email)s">%(email)s</a>&gt;')

    class ComposeAboutItem(Grimoire.Types.TextComposer.ComposeAboutItem):
        format = HtmlNoEscape("""%(name)s<br/>
<p>
 Version: %(versionname)s<br/>
 %(copychanges)s<br/>
 License: %(licenseURL)s
</p>
%(licenseText)s""")
