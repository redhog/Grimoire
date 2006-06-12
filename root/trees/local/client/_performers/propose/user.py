import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, types, ldap, os, string, time

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class user(Grimoire.Performer.Method):
        def _call(self, pnr, uid, userPassword):
            agreement = self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                    ['local', 'client', 'propose', 'agreement'], '/etc/Grimoire/client/agreement.tex', False))
            printer  = self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                    ['local', 'client', 'propose', 'agreement', 'printer'], '', False))

            attributes = Grimoire.Types.getValue(
                getattr(self._getpath(Grimoire.Types.MethodBase, 1).change.draftByPnr,
                        unicode(pnr))(uid=uid,
                                      userPassword=userPassword,
                                      DraftReady=''))

            cmd = 'cd /tmp;' + \
                  'sed ' + string.join(['-e "s+{\\\\[}%s{\\\\]}+%s+g"' % (key, Grimoire.Utils.encode(value[0], 'latin-1'))
                                        for key, value in attributes.items() + [('date', [time.strftime('%x')])]], ' ') + \
                  " < '%s' > 'agreement.tex';" % agreement + \
                  'latex /tmp/agreement.tex; dvips agreement.dvi;' + \
                  'lp %s agreement.ps' % ((printer and '-d ' + printer) or '')

            res = os.system(cmd)
            if res != 0:
                raise Exception(Grimoire.Types.Formattable('Printing of agreement failed with status %(status)s', status=res))

            return A(None, 'The agreement had been printed. Please sign it and hand it to the administrators')

        def _params(self):
            return A(Ps([('pnr', A(Grimoire.Types.NonemptyStringType,
                                   "Personal identification number")),
                         ('uid', A(Grimoire.Types.UsernameType,
                                   "Wanted account name")),
                         ('userPassword', A(Grimoire.Types.NewPasswordType,
                                            "Password for the new account")),
                         ]),
                     'Propose an account name and a password for your new account (a legal aggreement between you and the organization will be printed, which you will have to sign and give to the administration)')
        
