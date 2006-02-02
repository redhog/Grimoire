#! /usr/bin/python

if __name__ == '__main__':
    import ggui, Grimoire, gobject, gnome, gtk, gtk.glade, types, __main__, os.path

    program = gnome.program_init("Grimoire", "1.0")
    windows = gtk.glade.XML(os.path.join(os.path.split(ggui.__file__)[0], "ggui.glade"))

    aboutDialog =       windows.get_widget("aboutDialog")
    goToMethodDialog =  windows.get_widget("goToMethodDialog")
    treeViewType =      windows.get_widget("treeViewType")
    methodTreeView =    windows.get_widget("methodTreeView")
    objectTreeView =    windows.get_widget("objectTreeView")
    viewAsObjects =     windows.get_widget("viewAsObjects")
    location =          windows.get_widget("location")
    methodTitle =       windows.get_widget("methodTitle")
    methodOutput =      windows.get_widget("methodOutput")
    methodErrors =      windows.get_widget("methodErrors")
    methodParameters =  windows.get_widget("methodParameters")
    methodApplication = windows.get_widget("methodApplication")

    composer = Grimoire.Types.TextComposer
    session = None
    methodTreeView.append_column(gtk.TreeViewColumn("tree", gtk.CellRendererText(), markup=0))


    def argValues2Selections(argvalues, composer, optional = False):
        """Transforms a list of allowed values (from a ValuedType) into a
        list of comments
        """
        res = [composer(Grimoire.Types.getComment(argvalue, argvalue))
               for argvalue in argvalues]
        if optional:
            res.insert(0, composer('*No value specified*'))
        return res

    def paramsTypeObjectToFormFields(typeObj, composer):
        """Transforms a paramsTypeObject into a list of pairs of Gtk+
        labels and entry items suitable for input to the described
        function.
        """

        formDef = []
        argnum = 0

        for argpos in range(0, len(typeObj.arglist)):
            name, argtype = typeObj.arglist[argpos]
            comment = Grimoire.Types.getComment(argtype, name)
            argtype = Grimoire.Types.getValue(argtype)

            commentText = composer(comment)
            if argnum < typeObj.required:
                commentText = "<span foreground='#ff0000'>" + commentText + "</span>"
            commentWidget = gtk.Label(commentText)
            commentWidget.set_use_markup(True)

            argvalues = []
            while 1:
                if Grimoire.Utils.isDescendant(argtype, Grimoire.Types.HintedType):
                    argvalues += argtype.getValues()
                    argtype = argtype.parentType

                elif Grimoire.Utils.isDescendant(argtype, Grimoire.Types.NonemptyType):
                    argtype = argtype.parentType

                elif argtype is Grimoire.Types.AnyType or Grimoire.Utils.isDescendant(argtype, Grimoire.Types.ListType):
                    argtype = types.StringType
                    argvalues = map(repr, argvalues)
                    break
                else:
                    break

            if Grimoire.Utils.isDescendant(argtype, Grimoire.Types.RestrictedType):
                entryWidget = gtk.ComboBox()
                for argvalue in argValues2Selections(argtype.getValues(), composer, argpos >= typeObj.required):
                    entryWidget.append_text(argvalue)

            elif Grimoire.Utils.isDescendant(argtype, Grimoire.Types.BitfieldType):
                entryWidget = gtk.TreeView()
                for argvalue in argValues2Selections(argtype.getValues(), composer):
                    entryWidget.append_text(argvalue)

            elif Grimoire.Utils.isDescendant(argtype, Grimoire.Types.BooleanType):
                entryWidget = gtk.CheckButton()
                if argvalues and Grimoire.Types.getValue(argvalues[0]):
                    entryWidget.set_active(True)
                else:
                    entryWidget.set_active(False)

            elif Grimoire.Utils.isDescendant(argtype, Grimoire.Types.LoseNewPasswordType):
                entryWidget = gtk.Table(2, 2, True)
                entryWidget.attach(gtk.Label(composer('Once')), 0, 1, 0, 1)
                entryWidget.attach(gtk.Label(composer('Again')), 0, 1, 1, 2)
                entryWidget.attach(gtk.Entry(), 1, 2, 0, 1)
                entryWidget.attach(gtk.kEntry(), 1, 2, 1, 2)

            elif Grimoire.Utils.isDescendant(argtype, Grimoire.Types.LosePasswordType):
                entryWidget = gtk.Entry()
                entryWidget.set_visibility(False)

            elif Grimoire.Utils.isDescendant(argtype,
                                             types.StringType,
                                             types.IntType,
                                             types.UnicodeType,
                                             Grimoire.Types.UsernameType,
                                             Grimoire.Types.Ability.List):
                entryWidget = gtk.Entry()

            else:
                raise Exception("Unable to render input field for unknown type " + Grimoire.Utils.objInfo(typeObj.arglist[argpos][1]))

            commentWidget.show_all()
            commentWidget.set_alignment(0, 0)
            entryWidget.show_all()
            formDef += [(commentWidget, entryWidget)]
            argnum += 1
        return formDef

    class GrimoireTreeNode(object):
        def __init__(self, session, numpath):
            if numpath[0] != 0:
                raise IndexError
            self.session = session
            self.numpath = numpath
            self.node = session.dirCache
            self.path = []
            self.session.updatedDirCachePath(self.path, 1)
            for index in numpath[1:]:
                self.path.append(self.node.subNodes.__keys__[index])
                self.node = self.node.subNodes[self.path[-1]]
                self.session.updatedDirCachePath(self.path, 1)
        def __unicode__(self):
            if self.node.translation is not None:
                text = self.node.translation
            elif self.path:
                text = self.path[-1]
            else:
                text = 'Grimoire' 
            if not self.node.leaf:
                text = "<span foreground='#999999'>" + text + "</span>"
            return text

    class GrimoireTreeModel(gtk.GenericTreeModel):
        def __init__(self, session):
            '''constructor for the model.  Make sure you call
            PyTreeModel.__init__'''
            gtk.GenericTreeModel.__init__(self)
            self.session = session

        def on_get_flags(self):
            return 0
        def on_get_n_columns(self):
            return 1
        def on_get_column_type(self, index):
            return gobject.TYPE_STRING

        def on_get_path(self, node):
            return node.numpath
        def on_get_iter(self, path):
            return GrimoireTreeNode(self.session, path)
        def on_get_value(self, node, column):
            assert column == 0
            return unicode(node)
        def on_iter_next(self, node):
            try:
                return GrimoireTreeNode(self.session, node.numpath[:-1] +(node.numpath[-1]+1,))
            except IndexError:
                return None
        def on_iter_children(self, node):
            if node == None: # top of tree
                return GrimoireTreeNode(self.session, (0,))
            try:
                return GrimoireTreeNode(self.session, node.numpath +(0,))
            except IndexError:
                return None
        def on_iter_has_child(self, node):
            return len(node.node.subNodes)
        def on_iter_n_children(self, node):
            return len(node.node.subNodes)
        def on_iter_nth_child(self, node, n):
            if node == None:
                return GrimoireTreeNode(self.session, (n,))
            try:
                return GrimoireTreeNode(self.session, node.numpath +(n,))
            except IndexError:
                return None
        def on_iter_parent(self, node):
            if len(node.numpath) == 0:
                return None
            else:
                return GrimoireTreeNode(self.session, node.numpath[:-1])

    def on_newSession_activate(*arg, **kw):
        global session
        session = Grimoire._.clients.base()()
        methodTreeView.set_model(GrimoireTreeModel(session))

    def on_applyButton_clicked(button):
        print "apply"

    def on_methodTreeView_row_activated(treeView):
        numpath = treeView.get_cursor()[0]
        node = GrimoireTreeNode(treeView.get_model().session, numpath)
        if node.node.leaf:
            textPath = ".".join(['_'] + node.path)
            location.get_child().set_text(textPath)
            on_location_editing_done(location)

    def handleResult(result):
        pass

    def on_location_editing_done(location):
        text = location.get_child().get_text()
        location.prepend_text(text)
        try:
            method = session._.introspection.methodOfExpression(text, True)
        except Exception: # We've got a complex expression...
            method = None
        if method:
            typeObj = session.__._getpath(
                path=['introspection', 'params'] + list(method)
                )()
            formFields = paramsTypeObjectToFormFields(typeObj, composer)
            methodTitle.set_markup(Grimoire.Types.getComment(typeObj))
            methodTitle.show()
            methodOutput.hide()
            methodErrors.hide()
            if len(formFields):
                methodParameters.resize(len(formFields), 2)
                for child in methodParameters.get_children():
                    methodParameters.remove(child)
                for index, (label, entry) in enumerate(formFields):
                    methodParameters.attach(label, 0, 1, index, index + 1, gtk.FILL, 0)
                    methodParameters.attach(entry, 1, 2, index, index + 1, gtk.EXPAND | gtk.FILL, 0)
                methodParameters.show()
            else:
                methodParameters.hide()
        else:
            print "Except", text
            handleResult(session.eval(text))

    def on_about_activate(menu):
        aboutDialog.run()

    def on_goToMethod_activate(menu):
        goToMethodDialog.run()

    def on_viewAs_activate(menu):
        if menu.active:
            if viewAsObjects.active:
                treeViewType.set_current_page(1)
            else:
                treeViewType.set_current_page(0)

    def on_quit(*arg, **kw):
        gtk.main_quit()

    on_newSession_activate()
    windows.signal_autoconnect(__main__)
    gtk.main()
