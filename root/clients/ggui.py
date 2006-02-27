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
                # Fake - we'll override this with an instance
                # variable, but this makes it easy/fast to check if it
                # has been overridden...
                model = None 
                class View(FormSession.View, NumpathSession.View):
                    class DirCacheNode(FormSession.View.DirCacheNode, NumpathSession.View.DirCacheNode): pass

                    class GrimoireTreeModel(gtk.GenericTreeModel):
                        def __init__(self, view):
                            gtk.GenericTreeModel.__init__(self)
                            self.view = view
                            self.active = False

                        def update(self, modfn):
                            if self.active:
                                return modfn()
                            self.active = True
                            try:
                                return modfn()
                            finally:
                                self.active = False

                        def row_changed(self, path):
                            return super(Session.View.GrimoireTreeModel, self).row_changed(
                                path,
                                self.get_iter(path))

                        def row_inserted(self, path):
                            return super(Session.View.GrimoireTreeModel, self).row_inserted(
                                path,
                                self.get_iter(path))

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
                            return self.update(lambda:self.view.updateDirCacheNumPath(path[1:], 1))
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
                            return self.update(lambda:self.view.updateDirCache([], 1, 0, node))
                        def on_iter_children(self, node):
                            if node == None: return self.update(lambda:self.view.updateDirCache([], 1, 0))
                            try:
                                node = node.subNodes[node.subNodes.__keys__[0]]
                            except IndexError:
                                return None
                            return self.update(lambda:self.view.updateDirCache([], 1, 0, node))
                        def on_iter_has_child(self, node):
                            if node == None: True
                            return len(node.subNodes)
                        def on_iter_n_children(self, node):
                            if node == None: return 1
                            return len(node.subNodes)
                        def on_iter_nth_child(self, node, n):
                            if node == None:
                                assert n == 0
                                return self.update(lambda:self.view.updateDirCache([], 1, 0))
                            try:
                                node = node.subNodes[node.subNodes.__keys__[n]]
                            except IndexError:
                                return None
                            return self.update(lambda:self.view.updateDirCache([], 1, 0, node))
                        def on_iter_parent(self, node):
                            if node is None: return None
                            return node.parent

                    def __init__(self, *arg, **kw):
                        super(Session.View, self).__init__(*arg, **kw)
                        self.model = self.GrimoireTreeModel(self)
                        self.methodTreeView = self.session.methodTreeView
                        self.methodTreeView.set_model(self.model)
                        self.methodTreeView.connect("cursor_changed", self.selectionChanged)
                        self.location = self.session.location
                        self.location.child.connect("activate", self.locationChanged)
                        #self.location.connect("changed", self.locationChanged)
                        self.methodInteraction = self.session.methodInteraction

                    def insert(self, path, treeNode = None, root = False, **kw):
                        node = super(Session.View, self).insert(path, treeNode, root, **kw)
                        if self.model:
                            self.model.row_inserted((0,) + node.numpath)
                        return node
                    
                    def remove(self, path, treeNode = None, **kw):
                        node = self.getDirCacheNode(path, treeNode = treeNode)
                        if self.model:
                            self.model.row_deleted((0,) + node.numpath)
                        return super(Session.View, self).remove([], node, **kw)

                    def selectionChanged(self, methodTreeView):
                        numpath = methodTreeView.get_cursor()[0]
                        node = self.updateDirCacheNumPath(numpath[1:])
                        if node.leaf:
                            self.session.gotoLocation(node.path)

                    def locationChanged(self, *arg, **kw):
                        self.session.gotoLocation()

                def __init__(self, methodTreeView, location, methodInteraction, **kw):
                    self.methodTreeView = methodTreeView
                    self.location = location
                    self.methodInteraction = methodInteraction
                    class Composer(self.composer):
                        session = self
                    self.composer = Composer
                    super(Session, self).__init__(**kw)
                
                def insertUnique(self, path, obj, **kw):
                    upath = super(Session, self).insertUnique(path, obj, **kw)
                    for view in self.views.itervalues():
                        node = view.updateDirCachePath(upath)
                        view.methodTreeView.expand_to_path((0,) + node.numpath)
                    return upath

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

    def newSession(**kw):
        global session
        session = Grimoire._.clients.gnome(
            )(methodTreeView = methodTreeView, location = location,
              methodInteraction = methodInteraction,
              **kw)

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

    newSession(tree = (len(sys.argv) > 1 and sys.argv[1]),
               initCommands = sys.argv[2:])
    windows.signal_autoconnect(__main__)
    gtk.main()
