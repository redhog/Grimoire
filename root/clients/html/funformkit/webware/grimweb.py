import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, string, types, sys, traceback

debugParams = 1

class Performer(Grimoire.Performer.Base):
    class grimweb(Grimoire.Performer.Method):
        def _call(performer):
            FormPage = performer._callWithUnlockedTree(lambda: performer._getpath(Grimoire.Types.MethodBase)())

            class Grimweb(FormPage):
                def __init__(self):
                    FormPage.__init__(self, [])

                def parseCommand(self):
                    sess = self.grimoireSession()
                    fields = self.request().fields()

                    if fields == {}:
                        fields = {'select': 'default'}

                    if fields == sess.fields:
                        sess.invalidateDirCache()
                        self._formDefinitions = {}
                        fields = {}
                        submitted = 0
                        data = {}
                    else:
                        submitted, data = self.processForm()
                    sess.fields = fields

                    if submitted:
                        del data['submit']
                    if not submitted:
                        for key, value in fields.iteritems():
                            if key not in ('expand', 'expandPath', 'collapse', 'select'):
                                continue
                            method = performer._callWithUnlockedTree(lambda: performer._getpath(Grimoire.Types.MethodBase, 3).urlname.name2method(value))
                            if method is None:
                                method = sess.views[()].children[('tree',)].children[('methods',)].defaultMethod()
                                method = method and tuple(method)
                            if method is not None:
                                if key == 'expand':
                                    sess.views[()].children[('tree',)].children[('methods',)].expand(list(method), 1)
                                elif key == 'expandPath':
                                    sess.views[()].children[('tree',)].children[('methods',)].expandPath(list(method), 1)
                                elif key == 'collapse':
                                    sess.views[()].children[('tree',)].children[('methods',)].collapse(list(method))
                                elif key == 'select':
                                    sess.views[()].send.gotoPath(method)

                    if submitted:
                        sess.views[()].children[('selection',)].handleCall(args = data)
               
                def writeStyleSheet(self):
                    sess = self.grimoireSession()
                    self.writeln("""
                     <style type="text/css">
                      .menu {
                       background: url(%(menu)s);
                      }

                      .pageDividerV {
                       background: url(%(border_vertical)s);
                      }

                      .pageDividerH {
                       background: url(%(border_horizontal)s);
                      }
                     </style>
                    """ % {
                        'menu': sess.property_menu_bkr,
                        'border_horizontal': sess.property_border_horizontal,
                        'border_vertical': sess.property_border_middle,
                        })
                    self.writeln("<link rel='stylesheet' href='%(css)s' type='text/css'>" % {'css': unicode(self.grimoireSession().property_css)})

                def title(self):
                    return "The Grimoire action tree"

                def writeShortCutIcon(self):
                    self.writeln("<link rel='shortcut icon' href='%(icon)s'>" % {'icon': unicode(self.grimoireSession().property_mini_logo)})

                def writeContent(self):
                    sess = self.grimoireSession()

                    data = filter(lambda x: x,
                                  sess.views[()].children[('selection',)].renderSelection())

                    bordertopextension = """
                     <td class="pageDividerVExtension">
                      <img class="pageDividerVExtension" src="%(bordertopextension)s" alt="">
                     </td>
                     """ % {'bordertopextension': sess.property_border_top_extension}

                    if sess.views[()].children[('selection',)].method is not None:
                        relatedLink = """
                        <td class="relatedLink">
                         %(link)s
                        </td>
                        """ % {'link': self.getComposer()(Grimoire.Types.TitledURILink(
                            Grimoire.Types.GrimoireReference(['introspection', 'related'] + list(sess.views[()].children[('selection',)].method),
                                                             len(sess.views[()].children[('selection',)].method)),
                            'Related methods'))}
                    else:
                        relatedLink = ''
                    
                    if len(data) == 0:
                        dataTrs = bordertopextension
                    else:
                        dataTrs = string.join(
                            ["""
                             <tr class="formRow %(class)s">
                              %(head)s
                              <td class="formRow %(class)s" %(tdopts)s>
                               %(data)s
                              </td>
                              %(related)s
                             </tr>
                             """ % {'head': ['', bordertopextension][dataNr == 0],
                                    'class': [['formRowFirst', 'formRowFirst'],
                                                ['formRowMiddle', 'formRowLast']][dataNr != 0][dataNr == len(data) - 1],
                                    'tdopts': ['colspan=2', ''][dataNr == 0],
                                    'data': data[dataNr],
                                    'related': ['', relatedLink][dataNr == 0]}
                            for dataNr in xrange(0, len(data))],
                            """
                             <tr class="pageDividerH">
                              <td class="pageDividerH" colspan="3">
                               <img class="pageDividerH" src="%(border)s" alt="">
                              </td>
                             </tr>
                            """ % {'border': sess.property_border_horizontal})

                    self.writeln("""
                     <table class="main">
                      <tbody>
                       <tr>
                        <td class="menu" valign=top>
                         %(menu)s
                        </td>
                        <td class="pageDividerV">
                         <img class="pageDividerV" src="%(bordertop)s" alt="">
                        </td>
                        <td class="form">
                         <table class="form">
                          %(data)s
                         </table>
                        </td>
                       </tr>
                      </tbody>
                     </table>
                     """ % {'menu': self.grimoireSession().views[()].children[('tree',)].children[('methods',)].renderTreeToHtml(),
                            'data': dataTrs,
                            'bordertop': sess.property_border_top,
                            })

                def htBodyArgs(self):
                    return ''

                def writeDocType(self):
                    self.writeln('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">')
                    #self.writeln('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">')

                def reconnectGrimoire(self, *arg, **kw):
                    sess = FormPage.reconnectGrimoire(self, *arg, **kw)
                    sessvalue = Grimoire.Types.getValue(sess)
                    sessvalue.views[()].children[('selection',)].result = sessvalue.Result(
                        error = Exception("Your Grimoire login has expired and you have thus been logged out automatically"))
                    return sess

            return Grimweb

        _call = Grimoire.Utils.cachingFunction(_call)
        def _params(self):
            return A(Ps(),
                     'This is a full Grimoire client implemented using the WebWare WebKit and FunFormKit')
