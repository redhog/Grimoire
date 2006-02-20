#! /usr/bin/python

import _ggui.Composer, Grimoire, gobject, gnome, gtk, gtk.glade, types, sys
import Grimoire.Utils.Serialize.Writer, Grimoire.Utils.Serialize.Types, StringIO

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class gnome(Grimoire.Performer.Method):
        def _call(performer):
            NumpathSession = Grimoire._.clients.numpath()
            FormSession = Grimoire._.clients.form()
            class Session(FormSession, NumpathSession):
                composer = _ggui.Composer.GtkComposer
                sessionPath = FormSession.sessionPath + ['gnome']

                class GrimoireTreeModel(gtk.GenericTreeModel):
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
                        if node == None: ()
                        return node.numpath
                    def on_get_iter(self, path):
                        if path[0] != 0: raise IndexError
                        return self.session.updateDirCacheNumPath(path[1:], 1)
                    def on_get_value(self, node, column):
                        assert column == 0
                        return unicode(node)
                    def on_iter_next(self, node):
                        if node is None or node.parent is None:
                            return None
                        try:
                            node = node.parent.subNodes[
                                node.parent.subNodes.__keys__[node.numpath[-1] + 1]]
                        except IndexError:
                            return None
                        return self.session.updateDirCache([], 1, 0, node)
                    def on_iter_children(self, node):
                        if node == None: return self.session.updateDirCache([], 1, 0)
                        try:
                            node = node.subNodes[node.subNodes.__keys__[0]]
                        except IndexError:
                            return None
                        return self.session.updateDirCache([], 1, 0, node)
                    def on_iter_has_child(self, node):
                        if node == None: True
                        return len(node.subNodes)
                    def on_iter_n_children(self, node):
                        if node == None: return 1
                        return len(node.subNodes)
                    def on_iter_nth_child(self, node, n):
                        if node == None:
                            assert n == 0
                            return self.session.updateDirCache([], 1, 0)
                        try:
                            node = node.subNodes[node.subNodes.__keys__[n]]
                        except IndexError:
                            return None
                        return self.session.updateDirCache([], 1, 0, node)
                    def on_iter_parent(self, node):
                        if node is None: return None
                        return node.parent

                def __new__(cls, methodTreeView, location, methodInteraction, *arg, **kw):
                    self = super(Session, cls).__new__(cls, *arg, **kw)
                    self.methodTreeView = methodTreeView
                    self.methodTreeView.set_model(self.GrimoireTreeModel(self))
                    self.methodTreeView.connect("cursor_changed", self.selectionChanged)
                    self.location = location
                    self.location.child.connect("activate", self.locationChanged)
                    #self.location.connect("changed", self.locationChanged)
                    self.methodInteraction = methodInteraction
                    class Composer(cls.composer):
                        session = self
                    self.composer = Composer
                    return self

                def insertUnique(self, path, obj, treeNode = None, **kw):
                    upath = super(Session, self).insertUnique(path, obj, treeNode, **kw)
                    node = self.updateDirCachePath(upath, treeNode = treeNode)
                    model = self.methodTreeView.get_model()
                    model.row_inserted((0,) + node.numpath,
                                       model.get_iter((0,) + node.numpath))
                    if node.subNodes:
                        model.row_inserted((0,) + node.numpath + (0,),
                                           model.get_iter((0,) + node.numpath + (0,)))
                    self.methodTreeView.expand_to_path((0,) + node.numpath)
                    return upath

                def locationChanged(self, *arg, **kw):
                    self.gotoLocation()

                def selectionChanged(self, methodTreeView):
                    numpath = methodTreeView.get_cursor()[0]
                    node = self.updateDirCacheNumPath(numpath[1:])
                    if node.leaf:
                        self.gotoLocation(node.path)

                def gotoLocation(self, location = None):
                    if location:
                        if not Grimoire.Utils.isInstance(location, types.BaseStringType):
                            if Grimoire.Utils.isInstance(location, Grimoire.Types.GrimoireReference):
                                location = self.getMethodPath() + location
                                if location['levels']:
                                    raise ValueError("Bad reference")
                                location = location['path']
                            location = list(location)
                            expr = reduce(lambda expr, member:
                             Grimoire.Utils.Serialize.Types.Extension(
                              Grimoire.Utils.Serialize.Types.Member,
                              [expr,
                               Grimoire.Utils.Serialize.Types.Extension(
                                Grimoire.Utils.Serialize.Types.Identifier,
                                member)]),
                             location,
                             Grimoire.Utils.Serialize.Types.Extension(
                              Grimoire.Utils.Serialize.Types.Identifier,
                              "_"))
                            s = StringIO.StringIO()
                            Grimoire.Utils.Serialize.Writer.write(s, expr)
                            location = s.getvalue()
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
               initCommands = sys.argv[2:])
    windows.signal_autoconnect(__main__)
    gtk.main()
