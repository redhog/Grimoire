import Grimoire.Utils, Grimoire.Performer, Grimoire.Types, sys, string

profileRespond = False # 'respondprof-'


if profileRespond:
    import hotshot

class Performer(Grimoire.Performer.Base):
    class webware(Grimoire.Performer.Method):
        def _call(performer):
            import WebKit.Page
            
            FormServlet = performer._callWithUnlockedTree(lambda: performer._getpath(Grimoire.Types.MethodBase)())

            class FormPage(WebKit.Page.Page, FormServlet):
                def __init__(self, *arg, **kw):
                    FormServlet.__init__(self, *arg, **kw)
                    WebKit.Page.Page.__init__(self)
                    self.headers = {}
                    enc = sys.getdefaultencoding()
                    if enc.lower() in ('utf', 'utf8', 'utf-8'): enc = 'UTF-8'
                    self.headers['Content-Type'] = 'text/html; charset=%s' % enc
                    self.tmpHeaders = {}
                    self.responds = 0

                def setHeaders(self, **kw):
                    self.tmpHeaders = {}
                    self.tmpHeaders.update(kw)

                    for header in self.headers:
                        self.response().setHeader(header, self.headers[header])
                    for header in self.tmpHeaders:
                        self.response().setHeader(header, self.tmpHeaders[header])

                def respond(self, trans):
                    self.responds += 1
                    
                    def respond(self, trans):
                        if not self.isconnectedGrimoire():
                            self.connectGrimoire()
                        try:
                            self.setHeaders()
                            self.parseCommand()
                            WebKit.Page.Page.respond(self, trans)
                        except Exception, e:
                            import traceback
                            traceback.print_exc()

                            self.reconnectGrimoire()
                            self.response().reset()
                            self.setHeaders(Status='504 Grimoire login has expired')
                            req = self.request()
                            for key in req.fields().keys():
                                req.delField(key)
                            WebKit.Page.Page.respond(self, trans)

                    if profileRespond:
                        print "Respond:", self.responds
                        p = hotshot.Profile(profileRespond + str(self.responds))
                        try:
                            return p.runcall(respond, self, trans)
                        finally:
                            p.close()
                    else:
                        return respond(self, trans)

                def writeHeadParts(self):
                    self.writeHeaders()
                    self.writeTitle()
                    self.writeStyleSheet()
                    self.writeShortCutIcon()

                def writeHeaders(self):
                    self.writeln(
                        string.join(["<meta http-equiv='%s' content='%s'>" % header
                                     for header in self.headers.items() + self.tmpHeaders.items()], '\n'))

                def writeStyleSheet(self):
                    pass

                def title(self):
                    pass

                def writeShortCutIcon(self):
                    pass

                def parseCommand(self):
                    raise NotImplemented

            return FormPage

        _call = Grimoire.Utils.cachingFunction(_call)
        def _params(self):
            return A(Ps(),
                     'This is a WebWare WebKit page wrapper for a ClientSession that provides rendering of forms using FunFormKit')
