#! /usr/bin/python

import _ggui.Composer, Grimoire, gobject, gnome, gtk, gtk.glade, types, sys

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class gnome(Grimoire.Performer.Method):
        def _call(performer):
            class Session(Grimoire._.clients.form()):
                composer = _ggui.Composer.GtkComposer
                
                class GrimoireTreeModel(gtk.GenericTreeModel):
                    class GrimoireTreeNode(object):
                        def __init__(self, session, numpath = None, path = None):
                            if numpath is None and path is None:
                                raise ValueError
                            self.numpath = numpath
                            self.node = session.dirCache
                            self.path = path
                            if self.path is None:
                                self.path = []
                                if numpath[0] != 0:
                                    raise IndexError                            
                                session.updatedDirCachePath(self.path, 1)
                                for index in numpath[1:]:
                                    self.path.append(self.node.subNodes.__keys__[index])
                                    self.node = self.node.subNodes[self.path[-1]]
                                    session.updatedDirCachePath(self.path, 1)
                            else:
                                self.numpath = [0]
                                session.updatedDirCachePath(self.path, 1)
                                for item in self.path:
                                    self.numpath.append(self.node.subNodes.__keys__.index(item))
                                    self.node = self.node.subNodes[item]
                                self.numpath = tuple(self.numpath)
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

                    def __init__(self, session):
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
                        return self.GrimoireTreeNode(self.session, path)
                    def on_get_value(self, node, column):
                        assert column == 0
                        return unicode(node)
                    def on_iter_next(self, node):
                        try:
                            return self.GrimoireTreeNode(self.session, node.numpath[:-1] +(node.numpath[-1]+1,))
                        except IndexError:
                            return None
                    def on_iter_children(self, node):
                        if node == None: # top of tree
                            return self.GrimoireTreeNode(self.session, (0,))
                        try:
                            return self.GrimoireTreeNode(self.session, node.numpath + (0,))
                        except IndexError:
                            return None
                    def on_iter_has_child(self, node):
                        return len(node.node.subNodes)
                    def on_iter_n_children(self, node):
                        return len(node.node.subNodes)
                    def on_iter_nth_child(self, node, n):
                        if node == None:
                            return self.GrimoireTreeNode(self.session, (n,))
                        try:
                            return self.GrimoireTreeNode(self.session, node.numpath +(n,))
                        except IndexError:
                            return None
                    def on_iter_parent(self, node):
                        if len(node.numpath) == 0:
                            return None
                        else:
                            return self.GrimoireTreeNode(self.session, node.numpath[:-1])

                def __new__(cls, methodTreeView, location, methodInteraction, *arg, **kw):
                    self = super(Session, cls).__new__(cls, *arg, **kw)
                    self.methodTreeView = methodTreeView
                    self.methodTreeView.set_model(self.GrimoireTreeModel(self))
                    self.methodTreeView.connect("cursor_changed", self.selectionChanged)
                    self.location = location
                    self.methodInteraction = methodInteraction
                    class Composer(cls.composer):
                        session = self
                    self.composer = Composer
                    return self

                def insertUnique(self, path, obj, **kw):
                    upath = super(Session, self).insertUnique(path, obj, **kw)
                    node = self.GrimoireTreeModel.GrimoireTreeNode(self, path=upath)
                    model = self.methodTreeView.get_model()
                    model.row_inserted(node.numpath, model.get_iter(node.numpath))
                    #FIXME: What happens if obj has no children??
                    model.row_inserted(node.numpath + (0,), model.get_iter(node.numpath + (0,)))
                    self.methodTreeView.expand_to_path(node.numpath)
                    return upath

                def selectionChanged(self, methodTreeView):
                    numpath = methodTreeView.get_cursor()[0]
                    node = self.GrimoireTreeModel.GrimoireTreeNode(self, numpath)
                    if node.node.leaf:
                        self.gotoLocation(".".join(['_'] + node.path))

                def gotoLocation(self, location = None):
                    if location:
                        self.location.get_child().set_text(location)
                    else:
                        location = self.location.get_child().get_text()
                    self.location.prepend_text(location)
                    super(Session, self).gotoLocation(location)

                def drawSelection(self, selection):
                    self.methodInteraction.remove(self.methodInteraction.get_child())
                    self.methodInteraction.add(selection)
                    self.methodInteraction.show_all()

                def applyForm(self, form, args):
                    super(Session, self).applyForm(args)
                    
            return Session
        _call = Grimoire.Utils.cachingFunction(_call)
        def _params(self):
            return A(Ps(),
                     'This method returns a class nearly implementing a Gnome Grimoire client application.')

if __name__ == '__main__':
    import ggui, os.path, __main__

    program = gnome.program_init("Gnomoire", Grimoire.About.grimoireVersion)
    windows = gtk.glade.XML(os.path.join(os.path.split(ggui.__file__)[0], "_ggui", "ggui.glade"))

    aboutDialog =       windows.get_widget("aboutDialog")
    goToMethodDialog =  windows.get_widget("goToMethodDialog")
    treeViewType =      windows.get_widget("treeViewType")
    methodTreeView =    windows.get_widget("methodTreeView")
    objectTreeView =    windows.get_widget("objectTreeView")
    viewAsObjects =     windows.get_widget("viewAsObjects")
    location =          windows.get_widget("location")
    methodInteraction = windows.get_widget("methodInteraction")

    session = None
    methodTreeView.append_column(gtk.TreeViewColumn("tree", gtk.CellRendererText(), markup=0))

    def newSession(*arg, **kw):
        global session
        session = Grimoire._.clients.gnome(
            )(methodTreeView, location, methodInteraction, *arg, **kw)

    def on_newSession_activate(*arg, **kw):
        newSession()

    def on_applyButton_clicked(button):
        print "apply"

    def handleResult(result):
        pass

    def on_location_editing_done(location):
        session.gotoLocation()

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

    newSession((len(sys.argv) > 1 and sys.argv[1]),
               initCommands=sys.argv[2:])
    windows.signal_autoconnect(__main__)
    gtk.main()
