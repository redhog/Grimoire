import Grimoire, types, csv

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

# Format
# [client,                  server,  secret,  IP addresses]
# ['ryan@uanywhere.com.au', 'pptpd', 'xyzzy', '192.168.1.2']

class ChapSecrets(object):
    fieldnames = ['client', 'server', 'secret', 'ip']
    def __init__(self, path = '/etc/ppp/chap-secrets'):
        self.path = path
        self.items = {}
        for line in csv.DictReader(open(path, 'r'),
                                   delimiter=' ',
                                   fieldnames = self.fieldnames):
            if not line['client'] or line['client'] == '#': continue
            if line['server'] not in self.items: self.items[line['server']] = {}
            self.items[line['server']][line['client']] = line
    
    def save(self, path = None):
        path = path or self.path
        f = csv.DictWriter(open(path, 'w'), delimiter=' ', fieldnames = self.fieldnames)
        for perserver in self.items.itervalues():
            for item in perserver.itervalues():
                f.writerow(item)

class Performer(Grimoire.Performer.Base):
    class list_vpn_accounts(Grimoire.Performer.SubMethod):
        __path__ = ['list', 'vpn', 'accounts', '$processservername']
        __related_group__ = ['user']
        def _call(self, path, depth, convertToDirList = True):
            chapSecrets = ChapSecrets()
            if convertToDirList:
                return Grimoire.Performer.DirListFilter(
                    path, depth,
                    [(1, [item])
                     for item
                     in chapSecrets.items['pptpd'].iterkeys()])
            return chapSecrets.items

        def _dir(self, path, depth):
            return self._call(path, depth)

        def _params(self, path):
            return A(Ps([('depth',
                          A(types.IntType,
                            "Only return entries this far down in the tree (-1 means infinity)")),
                         ('convertToDirList',
                          A(Grimoire.Types.BooleanType,
                            "Convert entry listing to a Grimoire directory listing (that is, reverse and split DNs at ',')")),]),
                     'List vpn accounts')

    class create_vpn_account(Grimoire.Performer.Method):
        __path__ = ['create', 'vpn', 'account', '$processservername']
        __related_group__ = ['group']
        def _call(self, client, secret, ip = ''):
            chapSecrets = ChapSecrets()
            chapSecrets.items['pptpd'][client] = {'server': 'pptpd', 'client': client, 'secret': secret, 'ip': ip}
            chapSecrets.save()
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
            chapSecrets = ChapSecrets()
            del chapSecrets.items['pptpd'][path[0]]
            chapSecrets.save()
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
            chapSecrets = ChapSecrets()
            chapSecrets.items['pptpd'][path[0]]['secret'] = secret
            chapSecrets.items['pptpd'][path[0]]['ip'] = ip
            chapSecrets.save()
            return A(None,
                     'Account successfully saved')
            
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase,
                                      path = ['list', 'vpn', 'accounts', '$processservername'] + path
                                      )(depth))

        def _params(self, path):
            chapSecrets = ChapSecrets()
            item = chapSecrets.items['pptpd'][path[0]]
            return A(Ps([('secret', A(Grimoire.Types.HintedType.derive(Grimoire.Types.NewPasswordType,
                                                                       [item['secret']]),
                                      'Passphrase')),
                         ('ip', A(Grimoire.Types.HintedType.derive(types.StringType,
                                                                   [item['ip']]),
                                  'IP address of remote machine'))]),
                     Grimoire.Types.Formattable('Change VPN account %(client)s',
                                               client = path[0]))
