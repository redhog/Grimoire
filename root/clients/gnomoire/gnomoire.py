#! /usr/bin/python

profile = False # 'gnomoireprof'

import gnomoire, _gnomoire.Composer, Grimoire, Grimoire.Utils.Password, gobject, gnome, gtk, gtk.glade, types, sys, os.path

if profile:
    import hotshot

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class gnomoire(Grimoire.Performer.Method):
        __path__ = []
        def _call(performer):
            NumpathSession = Grimoire._.clients.numpath()
            FormSession = Grimoire._.clients.form()
            class Session(FormSession, NumpathSession):
                composer = _gnomoire.Composer.GtkComposer
                sessionPath = FormSession.sessionPath + ['gnome']

            class Client(object):
                def __init__(self, view, showMethodTree = False, showObjectTree = False, showMethodInteraction = False):
                    self.view = view
                    self.session = view.session
                    self.showMethodTree = showMethodTree
                    self.showObjectTree = showObjectTree
                    self.showMethodInteraction = showMethodInteraction
                    self.windows = gtk.glade.XML(os.path.join(os.path.split(gnomoire.__file__)[0], "_gnomoire", "gnomoire.glade"))

                    self.methodTreeView =    self.windows.get_widget("methodTreeView")
                    self.objectTreeView =    self.windows.get_widget("objectTreeView")
                    self.location =          self.windows.get_widget("location")
                    self.methodInteraction = self.windows.get_widget("methodInteraction")
                    self.relatedMethods =    self.windows.get_widget("relatedMethods")
                    
                    self.aboutDialog =        self.windows.get_widget("aboutDialog")
                    self.relatedMethodsItem = self.windows.get_widget("relatedMethodsItem")

                    self.windows.signal_autoconnect(self)
                    
                    if showMethodTree or showObjectTree:
                        treeViewType = self.windows.get_widget('treeViewType')
                        treeViewType.set_show_border(showMethodTree and showObjectTree)
                        treeViewType.set_show_tabs(showMethodTree and showObjectTree)
                        if not showMethodTree: treeViewType.set_current_page(1)
                        self.windows.get_widget('treeViewType').show()
                    if showMethodInteraction:
                        self.windows.get_widget('methodInteractionPane').show()
                    self.windows.get_widget('mainWindow').show()

                def on_openMethodsInNewWindow_toggled(self, menuItem):
                    self.view.send.setOpenMethodsInNewView(menuItem.get_active())

                def on_newSession_activate(self, *arg, **kw):
                    session = Grimoire._.clients.gnome(
                        )()
                    session.addView((), session.ClientView)

                def on_newView_activate(self, *arg, **kw):
                    self.session.addView(self.view.path + (Grimoire.Utils.Password.getasciisalt(16),), self.session.ClientView)

                def on_newTreeView_activate(self, *arg, **kw):
                    self.session.addView(self.view.path + (Grimoire.Utils.Password.getasciisalt(16),), self.session.CombinationView)

                def on_location_editing_done(self, location):
                    self.view.send.gotoLocation()

                def on_aboutGnomoire_activate(self, menu):
                    self.aboutDialog.run()

                def on_aboutGrimoire_activate(self, menu):
                    self.view.send.gotoLocation('_.about')

                def on_treeViewType_switch_page(self, treeViewType, page, pagenum):
                    if pagenum == 0:
                        self.relatedMethodsItem.child.set_markup_with_mnemonic("_Related methods")
                        self.relatedMethods.set_title("Related methods")
                    else:
                        self.relatedMethodsItem.child.set_markup_with_mnemonic("_Object methods")
                        self.relatedMethods.set_title("Object methods")

                def on_close(self, *arg, **kw):
                    if self.view.parent:
                        self.view.parent.deleteView(self.view.path)
                    else:
                        self.view.session.deleteView(self.view.path)
                    if not self.session.views:
                        gtk.main_quit()

            Session.Client = Client

            class Selection(FormSession.Selection):
                def __init__(self, location = None, methodInteraction = None, **kw):
                    super(Selection, self).__init__(**kw)
                    if not (location and methodInteraction):
                        self.makeGUI()
                    else:
                        self.location = location
                        self.methodInteraction = methodInteraction
                    self.location.child.connect("activate", self.locationChanged)

                def makeGUI(self):
                    self.client =   self.session.Client(self, showMethodInteraction = True)
                    self.location =          self.client.location
                    self.methodInteraction = self.client.methodInteraction

                def gotoLocation(self, location = None):
                    if location:
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

            class HoverSelection(FormSession.HoverSelection):
                def __init__(self, relatedMethods, **kw):
                    super(HoverSelection, self).__init__(**kw)
                    self.relatedMethods = relatedMethods
                
                def hoverPath(self, path, popup = None):
                    super(HoverSelection, self).hoverPath(path)
                    if popup:
                        self.relatedMethods.popup(None, None, None, popup.button, popup.time)

                def renderHoverSelection(self):
                    for child in self.relatedMethods.get_children():
                        self.relatedMethods.remove(child)
                        
                    composer = self.getComposer(self.method)

                    def addRelated(base, link):
                        comment = Grimoire.Types.getComment(link)
                        link = base + Grimoire.Types.getValue(link)
                        reference = gobject.GObject()
                        if link['levels']:
                            raise Exception(link)
                        reference.reference = link['path']
                            
                        def menuItemActivate(menuItem, reference):
                            self.send.gotoPath(reference.reference)
                        menuItem = gtk.MenuItem()
                        menuItem.add(composer(comment))
                        menuItem.connect('activate', menuItemActivate, reference)
                        self.relatedMethods.append(menuItem)

                    if self.method is not None:
                        if Grimoire.Utils.isPrefix(['introspection', 'object'], self.method):
                            for link in Grimoire.Types.getValue(self.session.__._getpath(path=self.method)()):
                                addRelated(self.method, link)
                        else:
                            for objectLinks in Grimoire.Types.getValue(self.session.__._getpath(path=['introspection', 'related'] + self.method)()):
                                for link in Grimoire.Types.getValue(objectLinks):
                                    addRelated(['introspection', 'related'] + self.method, link)
                    
                    self.relatedMethods.show_all()

            Session.HoverSelection = HoverSelection
            
            class MethodView(FormSession.TreeView, NumpathSession.TreeView):
                viewPath = ['methods']

                # Fake - we'll override this with an instance
                # variable, but this makes it easy/fast to check if it
                # has been overridden...
                model = None 

                class DirCacheNode(FormSession.TreeView.DirCacheNode, NumpathSession.TreeView.DirCacheNode): pass

                class TreeModel(gtk.GenericTreeModel):
                    def __init__(self, view):
                        gtk.GenericTreeModel.__init__(self)
                        self.view = view
                        self.setRootNode()

                    def setRootNode(self):
                        self.rootNode = self.view.updateDirCachePath([], 1, 0)

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

                def __init__(self, treeView = None, **kw):
                    super(MethodView, self).__init__(**kw)
                    if not treeView:
                        self.makeGUI()
                    else:
                        self.treeView = treeView
                    self.model = self.TreeModel(self)
                    self.treeView.append_column(gtk.TreeViewColumn("tree", gtk.CellRendererText(), markup=0))
                    self.treeView.set_model(self.model)
                    self.treeView.connect("row-activated", self.rowActivated)
                    self.treeView.connect("cursor-changed", self.rowSelected)
                    self.treeView.connect("button-press-event", self.rowExamined)

                def makeGUI(self):
                    self.client =   self.session.Client(self, showMethodTree = True)
                    self.treeView = self.client.methodTreeView

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

                def rowActivated(self, treeView, path, viewColumn):
                    self.send.selectionChanged(self.updateDirCacheNumPath(path[1:],
                                                                          treeNode = self.model.rootNode))

                def rowSelected(self, treeView):
                    self.send.hoverChanged(self.updateDirCacheNumPath(treeView.get_cursor()[0][1:],
                                                                      treeNode = self.model.rootNode))

                def rowExamined(self, widget, event):
                    if event.button == 3 and event.state == 0:
                        self.hoverChanged(self.updateDirCacheNumPath(self.treeView.get_path_at_pos(int(event.x), int(event.y))[0][1:],
                                                                     treeNode = self.model.rootNode),
                                          popup=event)
                        #return True
                    return False

            Session.MethodView = MethodView
            
            class ObjectView(MethodView):
                viewPath = ['objects']
                prefix = ['introspection', 'object']
                hide = Grimoire.Types.Ability.List([(Grimoire.Types.Ability.Ignore, ['introspection', 'object', 'object']),
                                                    (Grimoire.Types.Ability.Ignore, ['introspection', 'object', 'method']),
                                                    (Grimoire.Types.Ability.Ignore, ['introspection', 'object', '']),
                                                    (Grimoire.Types.Ability.Allow, ['introspection', 'object']),
                                                    (Grimoire.Types.Ability.Deny, [])])
                class TreeModel(MethodView.TreeModel): pass

                def makeGUI(self):
                    self.client =   self.session.Client(self, showObjectTree = True)
                    self.treeView = self.client.objectTreeView

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

            class CombinationView(FormSession.ViewGroup):
                def __init__(self, methodTreeView = None, objectTreeView = None, relatedMethods = None, **kw):
                    super(CombinationView, self).__init__(**kw)
                    if not (methodTreeView and objectTreeView and relatedMethods):
                        self.makeGUI()
                    else:
                        self.methodTreeView = methodTreeView
                        self.objectTreeView = objectTreeView
                        self.relatedMethods = relatedMethods
                    self.addView(('hover',), self.session.HoverSelection, relatedMethods = self.relatedMethods)
                    self.addView(('methods',), self.session.MethodView, treeView = self.methodTreeView)
                    self.addView(('objects',), self.session.ObjectView, treeView = self.objectTreeView)
                    
                def makeGUI(self):
                    self.client =         self.session.Client(view = self, showMethodTree = True, showObjectTree = True)
                    self.methodTreeView = self.client.methodTreeView
                    self.objectTreeView = self.client.objectTreeView
                    self.relatedMethods = self.client.relatedMethods
                    self.client.windows.get_widget("openMethodsInNewWindow").set_active(True)
                    self.send.setOenMethodsInNewWindow(True)

            Session.CombinationView = CombinationView

            class ClientView(FormSession.ViewGroup):
                def __init__(self, methodTreeView = None, objectTreeView = None, location = None, methodInteraction = None, relatedMethods = None, **kw):
                    super(ClientView, self).__init__(**kw)
                    if not (methodTreeView and objectTreeView and location and methodInteraction and relatedMethods):
                        self.makeGUI()
                    else:
                        self.methodTreeView =    methodTreeView
                        self.objectTreeView =    objectTreeView
                        self.location =          location
                        self.methodInteraction = methodInteraction
                        self.relatedMethods =    relatedMethods
                    self.addView(('tree',), self.session.CombinationView,
                                 methodTreeView = self.methodTreeView,
                                 objectTreeView = self.objectTreeView,
                                 relatedMethods = self.relatedMethods)
                    self.addView(('selection',), self.session.Selection,
                                 location = self.location,
                                 methodInteraction = self.methodInteraction)

                def makeGUI(self):
                    self.client =            self.session.Client(view = self, showMethodTree = True, showObjectTree = True, showMethodInteraction = True)
                    self.methodTreeView =    self.client.methodTreeView
                    self.objectTreeView =    self.client.objectTreeView
                    self.location =          self.client.location
                    self.methodInteraction = self.client.methodInteraction
                    self.relatedMethods =    self.client.relatedMethods


            Session.ClientView = ClientView
            
            return Session
        _call = Grimoire.Utils.cachingFunction(_call)
        def _params(self):
            return A(Ps(),
                     'This method returns a class nearly implementing a Gnome Grimoire client application.')

if __name__ == '__main__':
    program = gnome.program_init("Gnomoire", Grimoire.About.grimoireVersion)

    session = Grimoire._.clients.gnomoire(
        )(tree = (len(sys.argv) > 1 and sys.argv[1]),
          initCommands = sys.argv[2:])
    session.addView((), session.ClientView)
    
    if profile:
        p = hotshot.Profile(profile)
        try:
            p.runcall(gtk.main)
        finally:
            p.close()
    else:
        gtk.main()
