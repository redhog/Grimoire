import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, string, types, sys, traceback

debugParams = 1

class Performer(Grimoire.Performer.Base):
    class grimweb(Grimoire.Performer.Method):
        def _call(performer):
            FormPage = performer._callWithUnlockedTree(lambda: performer._getpath(Grimoire.Types.MethodBase)())
            Result = performer._callWithUnlockedTree(lambda: performer._getpath(levels=2).result())

            class Selection:
                def __init__(self):
                    self.method = None
                    self.form = None
                    self.result = None

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
                                method = sess.views[()].defaultMethod()
                                method = method and tuple(method)
                            if method is not None:
                                methodName = performer._callWithUnlockedTree(lambda: performer._getpath(Grimoire.Types.MethodBase, 3).urlname.method2name(method))
                                if key == 'expand':
                                    sess.expand(list(method), 1)
                                elif key == 'expandPath':
                                    sess.expandPath(list(method), 1)
                                elif key == 'collapse':
                                    sess.collapse(list(method))
                                elif key == 'select':
                                    sess.selection = Selection()
                                    sess.selection.method = method
                                    try:
                                        sess.selection.form = self.createForm(method)
                                        if sess.selection.form is None:
                                            submitted = 1
                                            data = {}
                                    except:
                                        if debugParams:
                                            traceback.print_exc()
                                        sess.selection.result = Result()
                                        sess.selection.result.error = sys.exc_info()[1]
                    if submitted:
                        sess.selection.result = self.handleCall(sess.selection.method, data)
                        if sess.selection.result.error is None:
                            sess.selection.form = None

                def renderMenu(self):
                    return self.grimoireSession().views[()].renderTreeToHtml()

                def renderFormTitle(self):
                    sess = self.grimoireSession()
                    if sess.selection is not None:
                        if sess.selection.form is not None:
                            return str(sess.getComposer()(
                                Grimoire.Types.Formattable(
                                    '%(comment)s:',
                                    comment=Grimoire.Types.getComment(
                                        self._params[sess.selection.method],
                                        Grimoire.Types.Reducible(sess.selection.method, ' ')))))
                        else:
                            return ''
                    return str(Composer('<b>Welcome to Grimoire.<br>Please select a method from the left.</b>'))

                def renderForm(self):
                    sess = self.grimoireSession()
                    if sess.selection is not None:
                        if sess.selection.form is not None:
                            return self.renderableForm(
                                formDefinition=sess.selection.form[0],
                                defaults=sess.selection.form[1]).htFormTable(
                                    bgcolor=self.grimoireSession().property_form_color)
                    return ''

                def renderError(self):
                    sess = self.grimoireSession()
                    if sess.selection is not None and sess.selection.result is not None and sess.selection.result.error is not None:
                        return ('<em class="errorMsg">%s.</em><br>' %
                                str(sess.getComposer()(sess.selection.result.error)))
                    return ''

                def renderResTitle(self):
                    sess = self.grimoireSession()
                    if sess.selection is not None and sess.selection.result is not None and sess.selection.result.result is not None:
                        comment = Grimoire.Types.getComment(sess.selection.result.result)
                        res = Grimoire.Types.getValue(sess.selection.result.result)
                        if comment is None and sess.selection.method is not None:
                            comment = Grimoire.Types.Formattable('%(method)s returned',
                                                                 method=Grimoire.Types.Reducible(sess.selection.method, ' '))
                        if comment is not None:
                            return str(sess.getComposer()(comment)) + [':', '.'][res is None]
                    return ''

                def renderRes(self):
                    sess = self.grimoireSession()
                    if sess.selection is not None and sess.selection.result is not None and sess.selection.result.result is not None:
                        res = Grimoire.Types.getValue(sess.selection.result.result)
                        if res is not None:
                            return str(sess.getComposer()(res))
                    return ''
                
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
                                  [self.renderError(), self.renderFormTitle(), self.renderForm(), self.renderResTitle(), self.renderRes()])

                    bordertopextension = """
                     <td class="pageDividerVExtension">
                      <img class="pageDividerVExtension" src="%(bordertopextension)s" alt="">
                     </td>
                     """ % {'bordertopextension': sess.property_border_top_extension}

                    if sess.selection and sess.selection.method is not None:
                        relatedLink = """
                        <td class="relatedLink">
                         %(link)s
                        </td>
                        """ % {'link': sess.getComposer()(Grimoire.Types.TitledURILink(
                            Grimoire.Types.GrimoireReference(['introspection', 'related'] + list(sess.selection.method),
                                                             len(sess.selection.method)),
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
                     """ % {'menu': self.renderMenu(),
                            'data': dataTrs,
                            'bordertop': sess.property_border_top,
                            })

                def htBodyArgs(self):
                    return ''

                def writeDocType(self):
                    self.writeln('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">')
                    #self.writeln('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">')

                def connectGrimoire(self, *arg, **kw):
                    sess = FormPage.connectGrimoire(self, *arg, **kw)
                    comment = Grimoire.Types.getComment(sess)
                    sessvalue = Grimoire.Types.getValue(sess)
                    sessvalue.selection = Selection()
                    sessvalue.selection.method = None
                    sessvalue.selection.result = performer._callWithUnlockedTree(lambda: performer._getpath(Grimoire.Types.MethodBase, 1).result())()
                    sessvalue.selection.result.result = Grimoire.Types.AnnotatedValue(None, comment)
                    return sess
                    
                def reconnectGrimoire(self, *arg, **kw):
                    sess = FormPage.reconnectGrimoire(self, *arg, **kw)
                    Grimoire.Types.getValue(sess).selection.result.error = Exception("Your Grimoire login has expired and you have thus been logged out automatically")
                    return sess

            return Grimweb

        _call = Grimoire.Utils.cachingFunction(_call)
        def _params(self):
            return A(Ps(),
                     'This is a full Grimoire client implemented using the WebWare WebKit and FunFormKit')
