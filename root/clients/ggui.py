#! /usr/bin/python

profile = False # 'gguiprof'

import _ggui.Composer, Grimoire, gobject, gnome, gtk, gtk.glade, types, sys
import Grimoire.Utils.Serialize.Writer, Grimoire.Utils.Serialize.Types, StringIO

if profile:
    import hotshot

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

            class Selection(FormSession.Selection):
                def __init__(self, session, path, location, methodInteraction, relatedMethods, **kw):
                    super(Selection, self).__init__(session, path, **kw)
                    self.location = location
                    self.location.child.connect("activate", self.locationChanged)
                    self.methodInteraction = methodInteraction
                    self.relatedMethods = relatedMethods
                    
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
                    super(Selection, self).gotoLocation(location)

                def drawSelection(self, selection):
                    self.methodInteraction.remove(self.methodInteraction.get_child())
                    self.methodInteraction.add(selection)
                    self.methodInteraction.show_all()

                def applyForm(self, form, args):
                    super(Selection, self).applyForm(args)

                def locationChanged(self, *arg, **kw):
                    self.gotoLocation()

            Session.Selection = Selection

            class MethodView(FormSession.View, NumpathSession.View):
                viewPath = ['methods']

                # Fake - we'll override this with an instance
                # variable, but this makes it easy/fast to check if it
                # has been overridden...
                model = None 

                class DirCacheNode(FormSession.View.DirCacheNode, NumpathSession.View.DirCacheNode): pass

                class TreeModel(gtk.GenericTreeModel):
                    prefix = []

                    def __init__(self, view):
                        gtk.GenericTreeModel.__init__(self)
                        self.view = view
                        self.setRootNode()

                    def setRootNode(self):
                        self.rootNode = self.view.updateDirCachePath(self.prefix, 1, 0)

                    def on_get_flags(self):
                        return 0
                    def on_get_n_columns(self):
                        return 1
                    def on_get_column_type(self, index):
                        return gobject.TYPE_STRING

                    def on_get_path(self, node):
                        if node == None: ()
                        return node.numpath[len(self.rootNode.numpath):]
                    def on_get_iter(self, path):
                        if path[0] != 0: raise IndexError
                        return self.view.updateDirCacheNumPath(path[1:], 1, treeNode = self.rootNode)
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
                        return self.view.updateDirCache([], 1, 0, node)
                    def on_iter_children(self, node):
                        if node == None: return self.rootNode
                        try:
                            node = node.subNodes[node.subNodes.__keys__[0]]
                        except IndexError:
                            return None
                        return self.view.updateDirCache([], 1, 0, node)
                    def on_iter_has_child(self, node):
                        if node == None: True
                        return len(node.subNodes)
                    def on_iter_n_children(self, node):
                        if node == None: return 1
                        return len(node.subNodes)
                    def on_iter_nth_child(self, node, n):
                        if node == None:
                            assert n == 0
                            return self.rootNode
                        try:
                            node = node.subNodes[node.subNodes.__keys__[n]]
                        except IndexError:
                            return None
                        return self.view.updateDirCache([], 1, 0, node)
                    def on_iter_parent(self, node):
                        if node is None: return None
                        return node.parent

                def __init__(self, treeView, **kw):
                    super(MethodView, self).__init__(**kw)
                    self.model = self.TreeModel(self)
                    self.treeView = treeView
                    self.treeView.append_column(gtk.TreeViewColumn("tree", gtk.CellRendererText(), markup=0))
                    self.treeView.set_model(self.model)
                    self.treeView.connect("row-activated", self.selectionChanged)

                def insert(self, path, treeNode = None, root = False, **kw):
                    node = super(MethodView, self).insert(path, treeNode, root, **kw)
                    self.model.row_inserted((0,) + node.numpath,
                                            self.model.get_iter((0,) + node.numpath))
                    self.treeView.expand_to_path((0,) + node.numpath)
                    return node

                def remove(self, path, treeNode = None, **kw):
                    node = self.getDirCacheNode(path, treeNode = treeNode)
                    self.model.row_deleted((0,) + node.numpath)
                    self.model.setRootNode()
                    return super(MethodView, self).remove([], node, **kw)

                def selectionChanged(self, treeView, path, viewColumn):
                    node = self.updateDirCacheNumPath(path[1:], treeNode = self.model.rootNode)
                    super(MethodView, self).selectionChanged(node)

            Session.MethodView = MethodView
            
            class ObjectView(MethodView):
                viewPath = ['objects']
                hide = Grimoire.Types.Ability.List([(Grimoire.Types.Ability.Ignore, ['introspection', 'object', 'object']),
                                                    (Grimoire.Types.Ability.Ignore, ['introspection', 'object', 'method']),
                                                    (Grimoire.Types.Ability.Allow, ['introspection', 'object']),
                                                    (Grimoire.Types.Ability.Deny, [])])
                class TreeModel(MethodView.TreeModel):
                    prefix = ['introspection', 'object']

                def insert(self, path, treeNode = None, root = False, **kw):
                    self.updateDirCachePath([], reupdate=1, treeNode = self.model.rootNode)
                    self.model.setRootNode()
                    self.model.row_deleted((0,))
                    self.model.row_inserted((0,), self.model.get_iter((0,)))
                    if self.model.rootNode.subNodes:
                        self.model.row_has_child_toggled((0,), self.model.get_iter((0,)))
                    return None

                def remove(self, path, treeNode = None, **kw):
                    self.updateDirCachePath([], reupdate=1, treeNode = self.model.rootNode)
                    self.model.setRootNode()
                    self.model.row_deleted((0,))
                    self.model.row_inserted((0,), self.model.get_iter((0,)))
                    if self.model.rootNode.subNodes:
                        self.model.row_has_child_toggled((0,), self.model.get_iter((0,)))
                    return None

            Session.ObjectView = ObjectView
            
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
    treeViewType =      windows.get_widget("treeViewType")
    methodTreeView =    windows.get_widget("methodTreeView")
    location =          windows.get_widget("location")
    relatedMethods =    windows.get_widget("relatedMethods")
    methodInteraction = windows.get_widget("methodInteraction")
    objectTreeView =    windows.get_widget("objectTreeView")
    viewAsObjects =     windows.get_widget("viewAsObjects")

    session = None

    def newSession(**kw):
        global session
        session = Grimoire._.clients.gnome(
            )(**kw)
        session.addView(('methods',), session.MethodView, treeView = methodTreeView)
        session.addView(('objects',), session.ObjectView, treeView = objectTreeView)
        session.addSelection(('main',), session.Selection,
                             location = location,
                             methodInteraction = methodInteraction,
                             relatedMethods = relatedMethods)
        session.connectViewAndSelection(('methods',), ('main',))
        session.connectViewAndSelection(('objects',), ('main',))
        
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

    if profile:
        p = hotshot.Profile(profile)
        try:
            p.runcall(gtk.main)
        finally:
            p.close()
    else:
        gtk.main()
