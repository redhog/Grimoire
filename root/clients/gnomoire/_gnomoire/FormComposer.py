import Grimoire.Types, gtk, gobject, types

Composer = Grimoire.Types.Composer.Composer
TextComposer = Grimoire.Types.TextComposer
ComposeObjType = Grimoire.Types.ComposeObjType
ComposeTypeType = Grimoire.Types.ComposeTypeType

def argValues2Selections(argvalues, composer, optional = False):
    """Transforms a list of allowed values (from a ValuedType) into a
    list of values and a list of of comments
    """
    values = [Grimoire.Types.getValue(argvalue, argvalue)
           for argvalue in argvalues]
    comments = [composer(Grimoire.Types.getComment(argvalue, argvalue))
           for argvalue in argvalues]
    if optional:
        comments.insert(0, composer('*No value specified*'))
    return values, comments

class ParamsFieldWidget(gtk.Table):
    def __init__(self, composer, obj, homogeneous=True):
        self.type = obj
        self.entries = {}
        fields = []
        def renderArglist(composer, arglist):
            for name, type in arglist:
                comment = Grimoire.Types.getComment(type, name)
                type = Grimoire.Types.getValue(type)
                self.entries[name] = composer(type)
                fields.append([composer(comment), self.entries[name]])
        class RequiredSubCompose(composer):
            labelFontAttributes = {'foreground': '#ff0000'}
        renderArglist(RequiredSubCompose, obj.arglist[:obj.required])
        if len(obj.arglist) > obj.required > 0:
            fields.append([gtk.HSeparator()])
        renderArglist(composer, obj.arglist[obj.required:])
        applyBox = gtk.HButtonBox()
        applyBox.set_layout(gtk.BUTTONBOX_END)
        applyButton = gtk.Button(stock="apply")
        applyButton.connect('clicked', self.__applyButtonClicked__)
        applyBox.pack_start(applyButton, False, False)
        fields.append([applyBox])
        width = max(map(len, fields))

        super(ParamsFieldWidget, self).__init__(len(fields), width, homogeneous)

        if composer.selection and composer.selection.applyForm:
            self.connect("applied", lambda form, args: composer.selection.applyForm(form, args.args))
        self.set_row_spacings(10)
        self.set_col_spacings(10)
        for line, field in enumerate(fields):
            yoptions = gtk.SHRINK | gtk.FILL
            xalign = yalign = 0
            xscale = 1
            yscale = 0
            if line == len(fields) - 1:
                yoptions = gtk.EXPAND | gtk.SHRINK | gtk.FILL
                xalign = yalign = 1
                xscale = 1
                yscale = 0
            for col, cell in enumerate(field):
                endcol = col + 1
                xoptions = gtk.SHRINK | gtk.FILL
                if col == len(field) - 1:
                    endcol = width
                    xoptions = gtk.EXPAND | gtk.SHRINK | gtk.FILL
                alignment = gtk.Alignment()
                alignment.set(xalign, yalign, xscale, yscale)
                alignment.add(cell)
                self.attach(alignment, col, endcol, line, line + 1, xoptions, yoptions)
    def __applyButtonClicked__(self, *arg, **kw):
        # Cludgy, but we _can't_ send a ParamsTypeObject just like
        # that since it's not a GObject...
        args = gobject.GObject()
        args.args = self.get_value()
        self.emit('applied', args)
    def get_value(self):
        kws = {}
        for name, entry in self.entries.iteritems():
           kws[name] = entry.get_value()
        return self.type([], [], kws, 0, 0, 1)
        
gobject.type_register(ParamsFieldWidget)
gobject.signal_new("applied", ParamsFieldWidget, gobject.SIGNAL_RUN_LAST | gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN, (gobject.GObject,))

class CommentedValuesModel(gtk.GenericTreeModel):
    def __init__(self, values, composer, optional = False):
        gtk.GenericTreeModel.__init__(self)
        self.values = values
        self.composer = composer
        self.optional = optional
        if optional:
            self.values = ['*No value specified*'] + self.values
        
    def on_get_flags(self):
        return 0
    def on_get_n_columns(self):
        return 1
    def on_get_column_type(self, index):
        return gobject.TYPE_STRING

    def on_get_path(self, node):
        return node
    def on_get_iter(self, path):
        return path
    def on_get_value(self, node, column):
        assert len(node) == 1 and column == 0
        return TextComposer(Grimoire.Types.getComment(self.values[node[0]], self.values[node[0]]))
    def on_iter_next(self, node):
        if node is None: return None
        assert len(node) == 1
        if node[0] + 1 < len(self.values):
            return (node[0] + 1,)
        return None
    def on_iter_children(self, node):
        if node == None and self.values:
            return (0,)
        return None
    def on_iter_has_child(self, node):
        if node == None:
            return len(self.values)
        return 0
    def on_iter_n_children(self, node):
        return self.on_iter_has_child(node)
    def on_iter_nth_child(self, node, n):
        if node == None and n < len(self.values):
            return (n,)
        return None
    def on_iter_parent(self, node):
        return None

class CommentedValuesTypeWidget(gtk.ComboBox):
    def __init__(self, values, composer, optional = False):
        super(CommentedValuesTypeWidget, self).__init__(
            CommentedValuesModel(values, composer, optional))
        cell = gtk.CellRendererText()
        self.pack_start(cell, True)
        self.add_attribute(cell, 'text', 0)
        self.values = values
        self.optional = optional

class RestrictedTypeWidget(CommentedValuesTypeWidget):
    def __init__(self, composer, obj):
        super(RestrictedTypeWidget, self).__init__(obj.getValues(), composer, composer.required)
    def get_value(self):
        if self.optional and self.get_active() == 0:
            raise ValueError
        return Grimoire.Types.getValue(self.values[self.get_active()])

class BitfieldTypeWidget(gtk.ComboBox):
    #FIXME: This should be a tree-widget so you can multi-select...
    def __init__(self, composer, obj):
        super(RestrictedTypeWidget, self).__init__()
        for argvalue in argValues2Selections(obj.getValues(), composer):
            self.append_text(argvalue)

class BooleanTypeWidget(gtk.CheckButton):
    def __init__(self, composer, obj):
        super(BooleanTypeWidget, self).__init__()
        if composer.defaultValues and Grimoire.Types.getValue(composer.defaultValues[0]):
            self.set_active(True)
        else:
            self.set_active(False)
    def get_value(self):
        return self.get_active()

class LoseNewPasswordTypeWidget(gtk.Table):
    def __init__(self, composer, obj):
        super(LoseNewPasswordTypeWidget, self).__init__(2, 2, True)
        self.attach(composer('Once'), 0, 1, 0, 1)
        self.attach(composer('Again'), 0, 1, 1, 2)
        self.entry1 = gtk.Entry()
        self.entry2 = gtk.Entry()
        self.entry1.set_visibility(False)
        self.entry2.set_visibility(False)
        self.attach(self.entry1, 1, 2, 0, 1)
        self.attach(self.entry2, 1, 2, 1, 2)
        if composer.defaultValues:
            self.set_text(TextComposer(Grimoire.Types.getValue(composer.defaultValues[0])))
    def set_text(self, text):
        self.entry1.set_text(text)
        self.entry2.set_text(text)
    def get_value(self):
        if self.entry1.get_text() != self.entry2.get_text():
            raise Exception("Entry inconsistency")
        return self.entry1.get_text()    

class StringTypeWidget(gtk.Widget):
    def __new__(cls, composer, obj):
        returnCls = cls
        if cls is StringTypeWidget:
            if len(composer.defaultValues) > 1:
                returnCls = MultipleStringTypeWidget
            else:
                returnCls = SingleStringTypeWidget
        return super(StringTypeWidget, cls).__new__(returnCls, composer, obj)
    def __init__(self, composer, obj):
        super(StringTypeWidget, self).__init__()
        if composer.defaultValues:
            self.set_text(TextComposer(Grimoire.Types.getValue(composer.defaultValues[0])))
    

class StringComboBoxEntry(gtk.ComboBoxEntry):
    def __init__(self, *arg, **kw):
        super(StringComboBoxEntry, self).__init__(gtk.ListStore(gobject.TYPE_STRING), 0)
    def set_text(self, text):
        self.child.set_text(text)
    def get_value(self):
        return self.child.get_text()

class MultipleStringTypeWidget(StringTypeWidget, StringComboBoxEntry):
    def __init__(self, composer, obj):
        super(MultipleStringTypeWidget, self).__init__(composer, obj)
        self.defaultValues = composer.defaultValues
        if self.defaultValues:
            self.set_active(0)
            for value in self.defaultValues:
                self.append_text(TextComposer(Grimoire.Types.getComment(value, value)))
    def get_value(self):
        if self.get_active() == -1:
            return super(MultipleStringTypeWidget, self).get_text()
        return Grimoire.Types.getValue(self.defaultValues[self.get_active()])

class SingleStringTypeWidget(StringTypeWidget, gtk.Entry):
    def get_value(self):
        return self.get_text()

class LosePasswordTypeWidget(SingleStringTypeWidget):
    def __init__(self, composer, obj):        
        super(LosePasswordTypeWidget, self).__init__(composer, obj)
        self.set_visibility(False)

class GtkFormComposer(Grimoire.Types.Composer.Composer):
    defaultValues = []
    required = False
    session = None
    
    class ComposeParamsType(ComposeTypeType):
        type = Grimoire.Types.GenericParamsType
        compose = ParamsFieldWidget

    class ComposeHintedType(ComposeTypeType):
        type = Grimoire.Types.GenericHintedType
        def compose(cls, composer, obj):
            class Composer(composer):
                __name__ = 'Hinted' + composer.__name__
                defaultValues = obj.getValues()
            return Composer(obj.parentType)

    class ComposeNonemptyType(ComposeTypeType):
        type = Grimoire.Types.GenericNonemptyType
        def compose(cls, composer, obj):
            return composer(obj.parentType)

    class ComposeAnyType(ComposeTypeType):
        type = Grimoire.Types.AnyType
        def compose(cls, composer, obj):
            class Composer(composer):
                __name__ = 'Any' + composer.__name__
                defaultValues = map(repr, composer.defaultValues)
            return Composer(types.StringType)

    class ComposeListType(ComposeAnyType):
        type = Grimoire.Types.ListType

    class ComposeRestrictedType(ComposeTypeType):
        type = Grimoire.Types.GenericRestrictedType
        compose = RestrictedTypeWidget
        
    class ComposeBitfieldType(ComposeTypeType):
        type = Grimoire.Types.BitfieldType
        compose = BitfieldTypeWidget

    class ComposeBooleanType(ComposeTypeType):
        type = Grimoire.Types.BooleanType
        compose = BooleanTypeWidget

    class ComposeLoseNewPasswordType(ComposeTypeType):
        type = Grimoire.Types.LoseNewPasswordType
        compose = LoseNewPasswordTypeWidget
        
    class ComposeLosePasswordType(ComposeTypeType):
        type = Grimoire.Types.LosePasswordType
        compose = LosePasswordTypeWidget

    class ComposeStringType(ComposeTypeType):
        type = types.StringType
        compose = StringTypeWidget

    class ComposeUnicodeType(ComposeStringType):
        type = types.UnicodeType

    class ComposeIntType(ComposeStringType):
        type = types.IntType

    class ComposeUsernameType(ComposeStringType):
        type = Grimoire.Types.UsernameType

    class ComposeAbilityListType(ComposeStringType):
        type = Grimoire.Types.Ability.List
