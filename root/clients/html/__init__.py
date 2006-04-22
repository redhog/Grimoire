import Grimoire.Performer, Grimoire.Utils, Grimoire.Types, string

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive
enc = Grimoire.Utils.encode


debugTree = 0


class Performer(Grimoire.Performer.Base):
    class html(Grimoire.Performer.Method):
        def _call(performer):
            RenderableSession = performer._callWithUnlockedTree(
                lambda: performer._getpath(Grimoire.Types.MethodBase).renderable())
            FormSession = performer._callWithUnlockedTree(
                lambda: performer._getpath(Grimoire.Types.MethodBase).form())
            class Session(RenderableSession, FormSession):
                sessionPath = FormSession.sessionPath + ['html']

                class TreeView(RenderableSession.TreeView, FormSession.TreeView):
                    def renderTreeToHtml(self):
                        if debugTree:
                            print "RenderTree:"
                            print self.renderTreeToText()


                        def renderEntry(node, sibling, res, indent=''):
                            path = node.path
                            siblings = node.parent and len(node.parent.subNodes) or 1
                            subNodes = len(node.subNodes)

                            res = (res or '') + '<div class="menuRow">' + indent
                            res += '<span class="%s">' % ['shadedMenuItem', 'menuItem'][node.leaf]

                            method = performer._callWithUnlockedTree(lambda: performer._getpath(Grimoire.Types.MethodBase).urlname.method2name(path))

                            if subNodes or not node.updated:
                                res += "<a href='%(url)s?%(command)s=%(method)s'>" % {
                                    'url': enc(self.session.pageurl),
                                    'command': ['expand', 'collapse'][node.expanded],
                                    'method': method}
                            res += self.session.pictExpander[subNodes > 0 or not node.updated][node.expanded][sibling == siblings - 1]
                            if subNodes or not node.updated:
                                res += '</a>'

                            if node.leaf:
                                res += "<a href='%(url)s?select=%(method)s'>" % {
                                    'url': enc(self.session.pageurl),
                                    'method': method
                                    }

                            res += self.session.pictIcon[subNodes > 0][node.expanded]
                            if node.translation is not None:
                                res += enc(node.translation)
                            elif path:
                                res += enc(path[-1])
                            else:
                                res += 'Grimoire'

                            if node.leaf:
                                res += '</a>'
                            res += "</span></div>\n"
                            return (res,
                                    (' ' + indent + self.session.pictIndent[sibling == siblings - 1],),
                                    {})

                        return self.renderTree(renderEntry, '    ')
                    
                def __init__(self, *arg, **kw):
                    super(Session, self).__init__(*arg, **kw)
                    params = Grimoire._.directory.get.parameters
                    self.pageurl = params.clients.html(['url'])
                    self.baseurl = params.clients.html(['static', 'url'], self.pageurl, 0)

                    self.pageurl = Grimoire.Types.URI(self.pageurl)
                    self.baseurl = Grimoire.Types.URI(self.baseurl)

                    self.property_css = self.baseurl + 'Grimweb.css'
                    try:
                        self.property_pictureUrl = Grimoire.Types.URI(
                            params(
                                ['clients', 'html', 'theme', 'pictures', 'url']))
                    except (AttributeError, TypeError):
                        self.property_pictureUrl = self.baseurl + 'pictures'
                    self.property_picturePattern = params(
                        ['clients', 'html', 'theme', 'pictures', 'pattern'], "grime.%(name)s.png", 0)
                    self.property_menu_bkr = enc(self.property_pictureUrl + (self.property_picturePattern % {'name': 'linkbkr'}))
                    self.property_border_top = enc(self.property_pictureUrl + (self.property_picturePattern % {'name': 'border.top'}))
                    self.property_border_top_extension = enc(self.property_pictureUrl + (self.property_picturePattern % {'name': 'border.top.extension'}))
                    self.property_border_middle = enc(self.property_pictureUrl + (self.property_picturePattern % {'name': 'border.middle'}))
                    self.property_border_horizontal = enc(self.property_pictureUrl + (self.property_picturePattern % {'name': 'border.horizontal'}))
                    self.property_mini_logo = enc(self.property_pictureUrl + (self.property_picturePattern % {'name': 'mini-logo'}))
                    self.property_form_color = params(['clients', 'html', 'theme', 'form', 'box', 'colour'], "#ffffff", 0)

                    def img(name, alt):
                        return "<img class='menuIcon' src='%(src)s' alt='%(alt)s'>" % {
                            'src': enc(self.property_pictureUrl + (self.property_picturePattern % {'name': name})),
                            'alt': alt
                            }
                    self.pictIcon = ((img('doc', '[=]'),
                                      img('doc', '[=]')),
                                     (img('dir', '\\_\\'),
                                      img('dir.open', '\\_/')))            
                    self.pictExpander = (((img('middle', '|--'),
                                           img('end', '`--')),
                                          (img('middle', '|--'),
                                           img('end', '`--'))),
                                         ((img('middle.expandable', '|-+'),
                                           img('end.expandable', '`-+')),
                                          (img('middle.expanded', '|--'),
                                           img('end.expanded', '`--'))))

                    self.pictIndent = (img('vertical', '|&nbsp;&nbsp;'),
                                       img('empty', '&nbsp;&nbsp;&nbsp;'))


                    class Composer(Grimoire.Types.HtmlComposer):
                        methodBaseURI = '%s?select=%%(method)s' % enc(self.pageurl)

                    self.composer = Composer

                    self.expand([], 1)
                    if debugTree:
                        print "Boot:"
                        print self.renderTreeToText()
            return Session
        _call = Grimoire.Utils.cachingFunction(_call)
        def _params(self):
            return A(Ps(),
                     'A renderable session that can render to HTML, and that reads in a lot of configuration data for the rendering of various HTML components')

