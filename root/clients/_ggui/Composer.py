import Grimoire.Types, FormComposer, gtk, gobject, xml.sax.saxutils

Composer = Grimoire.Types.Composer.Composer
ComposeObjType = Grimoire.Types.ComposeObjType
ComposeTypeType = Grimoire.Types.ComposeTypeType
TextComposer = Grimoire.Types.TextComposer

class StringWidget(gtk.Label):
    def __init__(self, composer, obj):
        super(StringWidget, self).__init__()
        self.set_line_wrap(True)
        self.set_alignment(0, 0)
        class ParentComposer(composer.parameters(), TextComposer): pass
        self.set_markup(
            '<span %s>%s</span>' % (
                ' '.join('%s="%s"' % item for item in composer.labelFontAttributes.iteritems()),
                xml.sax.saxutils.escape(ParentComposer(obj))))

class BlockWidget(gtk.HBox):
    def __init__(self, composer, blocks):
        super(BlockWidget, self).__init__()
        self.set_spacing(0)
        for block in blocks:
            self.pack_start(composer(block), False, True)

class LinesWidget(gtk.VBox):
    def __init__(self, composer, lines):
        super(LinesWidget, self).__init__()
        self.set_spacing(0)
        for line in lines:
            self.pack_start(composer(line), False, True)

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

class TitledURILinkWidget(gtk.Button):
    def __init__(self, composer, obj):
        super(TitledURILinkWidget, self).__init__()
        self.add(composer(Grimoire.Types.getComment(obj)))
        class ParentComposer(composer.parameters(), TextComposer): pass
        self.target = Grimoire.Types.getValue(obj)
        self.connect('clicked', self.__clicked__)
        if Grimoire.Utils.isInstance(self.target, Grimoire.Types.GrimoireReference):
            if composer.selection and composer.selection.gotoPath:
                self.connect('selected',
                             lambda link, target: composer.selection.gotoPath((composer.selection.method + target.target)['path']))
    def __clicked__(self, button):
        target = gobject.GObject()
        target.target = self.target
        self.emit("selected", target)

gobject.type_register(TitledURILinkWidget)
gobject.signal_new("selected", TitledURILinkWidget, gobject.SIGNAL_RUN_LAST | gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN, (gobject.GObject,))

class GtkComposer(FormComposer.GtkFormComposer, Grimoire.Types.TextComposer.wrap()):
    labelFontAttributes = {}

    class ComposeString(TextComposer.ComposeString):
        compose = StringWidget

    class ComposeBlock(TextComposer.ComposeBlock):
        compose = BlockWidget

    class ComposeLines(TextComposer.ComposeLines):
        compose = LinesWidget

    class ComposeParagraphs(TextComposer.ComposeParagraphs):
        compose = ParagraphsWidget

    class ComposeAnnotatedValue(TextComposer.ComposeAnnotatedValue):
        compose = AnnotatedValueWidget

    class ComposeTitledURILink(TextComposer.ComposeGenericMapping):
        type = Grimoire.Types.TitledURILink
        compose = TitledURILinkWidget
        
#     class ComposeGrimoireReference(TextComposer.ComposeGrimoireReference):
#         def compose(cls, composer, obj):
#             return composer.methodBaseURI % {
#                 'method': urllib.quote_plus(Grimoire.Utils.encode(
#                     "." +  TextComposer.ComposeGrimoireReference.compose(composer, obj)))}
