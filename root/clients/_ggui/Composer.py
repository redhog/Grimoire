import Grimoire.Types, FormComposer, gtk, xml.sax.saxutils

Composer = Grimoire.Types.Composer.Composer
ComposeObjType = Grimoire.Types.ComposeObjType
ComposeTypeType = Grimoire.Types.ComposeTypeType
TextComposer = Grimoire.Types.TextComposer

class StringWidget(gtk.Label):
    def __init__(self, composer, obj):
        super(StringWidget, self).__init__()
        self.set_line_wrap(True)
        self.set_alignment(0, 0)
        self.set_markup(
            '<span %s>%s</span>' % (
                ' '.join('%s="%s"' % item for item in composer.labelFontAttributes.iteritems()),
                xml.sax.saxutils.escape(TextComposer(obj))))

class ParagraphsWidget(gtk.VBox):
    def __init__(self, composer, paragraphs):
        super(ParagraphsWidget, self).__init__()
        self.set_spacing(10)
        for paragraph in paragraphs:
            self.pack_start(composer(paragraph), False, True)

class AnnotatedValueWidget(gtk.Widget):
    def __new__(cls, composer, obj):
        returnCls = cls
        if cls is AnnotatedValueWidget:
            if Grimoire.Types.getValue(obj) is None:
                returnCls = AnnotatedNoneWidget
            else:
                returnCls = AnnotatedSomethingWidget
        return super(AnnotatedValueWidget, cls).__new__(returnCls, composer, obj)
    
class AnnotatedNoneWidget(AnnotatedValueWidget, StringWidget):
    def __init__(self, composer, obj):
        super(AnnotatedNoneWidget, self).__init__(
            composer,
            Grimoire.Types.Formattable("%(comment)s.", comment = Grimoire.Types.getComment(obj)))
            
class AnnotatedSomethingWidget(AnnotatedValueWidget, gtk.Frame):
    def __init__(self, composer, obj):
        super(AnnotatedValueWidget, self).__init__()
        self.set_label_widget(composer(
            Grimoire.Types.Formattable("%(comment)s:",
                                       comment = Grimoire.Types.getComment(obj))))
        self.get_label_widget().set_line_wrap(True)
        self.set_label_align(0, 1)
        alignment = gtk.Alignment()
        alignment.set(0, 0, 1, 1)
        alignment.set_padding(10, 10, 10, 10)
        alignment.add(composer(Grimoire.Types.getValue(obj)))
        self.add(alignment)        

class GtkComposer(FormComposer.GtkFormComposer, Grimoire.Types.TextComposer.wrap()):
    labelFontAttributes = {}

    class ComposeString(TextComposer.ComposeString):
        compose = StringWidget

    class ComposeParagraphs(TextComposer.ComposeParagraphs):
        compose = ParagraphsWidget

    class ComposeAnnotatedValue(TextComposer.ComposeAnnotatedValue):
        compose = AnnotatedValueWidget

#     class ComposeTitledURILink(TextComposer.ComposeGenericMapping):
#         type = Composable.TitledURILink
#         def compose(cls, composer, obj):
        
#     class ComposeGrimoireReference(TextComposer.ComposeGrimoireReference):
#         def compose(cls, composer, obj):
#             return composer.methodBaseURI % {
#                 'method': urllib.quote_plus(Grimoire.Utils.encode(
#                     "." +  TextComposer.ComposeGrimoireReference.compose(composer, obj)))}
