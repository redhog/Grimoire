#### fixme ####
# description = """Integrate this code with ppp.py /
# change.ppp.account etc - this is really duplicate code because I'm
# lazy ATM."""
#### end ####

import Grimoire, types, csv
from Grimoire.root.trees.local.process._performers._ppp import ChapSecrets

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class list_vpn_accounts(Grimoire.Performer.SubMethod):
        __path__ = ['list', 'vpn', 'accounts', '$processservername']
        __related_group__ = ['user']
        def _call(self, path, depth, convertToDirList = True):
            if convertToDirList:
                return Grimoire.Performer.DirListFilter(
                    path, depth,
                    [(1, [item])
                     for item
                     in ChapSecrets.chapSecrets.items['pptpd'].iterkeys()])
            return ChapSecrets.chapSecrets.items['pptpd']

        def _dir(self, path, depth):
            return self._call(path, depth)

        def _params(self, path):
            return A(Ps([('depth',
                          A(types.IntType,
                            "Only return entries this far down in the tree (-1 means infinity)")),
                         ('convertToDirList',
                          A(Grimoire.Types.BooleanType,
                            "Convert entry listing to a Grimoire directory listing")),]),
                     'List vpn accounts')

    class create_vpn_account(Grimoire.Performer.Method):
        __path__ = ['create', 'vpn', 'account', '$processservername']
        __related_group__ = ['group']
        def _call(self, client, secret, ip = ''):
            ChapSecrets.chapSecrets.items['pptpd'][client] = {'server': 'pptpd', 'client': client, 'secret': secret, 'ip': ip}
            ChapSecrets.chapSecrets.save()
            return A(None,
                     'Account successfully added')
        
        def _params(self):
            return A(Ps([('client', A(Grimoire.Types.NonemptyStringType,
                                      'Client address (username@host)')),
                         ('secret', A(Grimoire.Types.NewPasswordType,
                                      'Passphrase')),
                         ('ip', A(types.StringType,
                                  'IP address of remote machine'))]),
                     'Add a VPN account')
        
    class delete_vpn_account(Grimoire.Performer.SubMethod):
        __path__ = ['delete', 'vpn', 'account', '$processservername']
        __related_group__ = ['user']
        def _call(self, path):
            del ChapSecrets.chapSecrets.items['pptpd'][path[0]]
            ChapSecrets.chapSecrets.save()
            return A(None,
                     'Account successfully deleted')
            
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase,
                                      path = ['list', 'vpn', 'accounts', '$processservername'] + path
                                      )(depth))

        def _params(self, path):
            return A(Ps([]),
                     'Delete VPN account')

    class change_vpn_account(Grimoire.Performer.SubMethod):
        __path__ = ['change', 'vpn', 'account', '$processservername']
        __related_group__ = ['user']
        def _call(self, path, secret, ip = ''):
            ChapSecrets.chapSecrets.items['pptpd'][path[0]]['secret'] = secret
            ChapSecrets.chapSecrets.items['pptpd'][path[0]]['ip'] = ip
            ChapSecrets.chapSecrets.save()
            return A(None,
                     'Account successfully saved')
            
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase,
                                      path = ['list', 'vpn', 'accounts', '$processservername'] + path
                                      )(depth))

        def _params(self, path):
            item = ChapSecrets.chapSecrets.items['pptpd'][path[0]]
            return A(Ps([('secret', A(Grimoire.Types.HintedType.derive(Grimoire.Types.NewPasswordType,
                                                                       [item['secret']]),
                                      'Passphrase')),
                         ('ip', A(Grimoire.Types.HintedType.derive(types.StringType,
                                                                   [item['ip']]),
                                  'IP address of remote machine'))]),
                     Grimoire.Types.Formattable('Change VPN account %(client)s',
                                               client = path[0]))
