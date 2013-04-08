import Grimoire, types, csv
from Grimoire.root.trees.local.process._performers._ppp import ChapSecrets

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class list_ppp_accounts(Grimoire.Performer.SubMethod):
        __path__ = ['list', 'ppp', 'accounts', '$processservername']
        __related_group__ = ['user']
        def _call(self, path, depth, convertToDirList = True):
            if convertToDirList:
                items = []
                for server, byserver in ChapSecrets.chapSecrets.items.iteritems():
                    for client in byserver.iterkeys():
                        items.append((1, [server, client]))
                return Grimoire.Performer.DirListFilter(
                    path, depth, items)
            return ChapSecrets.chapSecrets.items

        def _dir(self, path, depth):
            return self._call(path, depth)

        def _params(self, path):
            return A(Ps([('depth',
                          A(types.IntType,
                            "Only return entries this far down in the tree (-1 means infinity)")),
                         ('convertToDirList',
                          A(Grimoire.Types.BooleanType,
                            "Convert entry listing to a Grimoire directory listing")),]),
                     'List ppp accounts')

    class create_ppp_account(Grimoire.Performer.Method):
        __path__ = ['create', 'ppp', 'account', '$processservername']
        __related_group__ = ['group']
        def _call(self, server, client, secret, ip = ''):
            if server not in ChapSecrets.chapSecrets.items:
                ChapSecrets.chapSecrets.items[server] = {}
            ChapSecrets.chapSecrets.items[server][client] = {'server': server, 'client': client, 'secret': secret, 'ip': ip}
            ChapSecrets.chapSecrets.save()
            return A(None,
                     'Account successfully added')
        
        def _params(self):
            return A(Ps([('server', A(Grimoire.Types.NonemptyStringType,
                                      'Server name')),
                         ('client', A(Grimoire.Types.NonemptyStringType,
                                      'Client address (username@host)')),
                         ('secret', A(Grimoire.Types.NewPasswordType,
                                      'Passphrase')),
                         ('ip', A(types.StringType,
                                  'IP address of remote machine'))]),
                     'Add a PPP account')
        
    class delete_ppp_account(Grimoire.Performer.SubMethod):
        __path__ = ['delete', 'ppp', 'account', '$processservername']
        __related_group__ = ['user']
        def _call(self, path):
            del ChapSecrets.chapSecrets.items[path[0]][path[1]]
            ChapSecrets.chapSecrets.save()
            return A(None,
                     'Account successfully deleted')
            
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase,
                                      path = ['list', 'ppp', 'accounts', '$processservername'] + path
                                      )(depth))

        def _params(self, path):
            return A(Ps([]),
                     'Delete PPP account')

    class change_ppp_account(Grimoire.Performer.SubMethod):
        __path__ = ['change', 'ppp', 'account', '$processservername']
        __related_group__ = ['user']
        def _call(self, path, secret, ip = ''):
            ChapSecrets.chapSecrets.items[path[0]][path[1]]['secret'] = secret
            ChapSecrets.chapSecrets.items[path[0]][path[1]]['ip'] = ip
            ChapSecrets.chapSecrets.save()
            return A(None,
                     'Account successfully saved')
            
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase,
                                      path = ['list', 'ppp', 'accounts', '$processservername'] + path
                                      )(depth))

        def _params(self, path):
            item = ChapSecrets.chapSecrets.items[path[0]][path[1]]
            return A(Ps([('secret', A(Grimoire.Types.HintedType.derive(Grimoire.Types.NewPasswordType,
                                                                       [item['secret']]),
                                      'Passphrase')),
                         ('ip', A(Grimoire.Types.HintedType.derive(types.StringType,
                                                                   [item['ip']]),
                                  'IP address of remote machine'))]),
                     Grimoire.Types.Formattable('Change PPP account %(client)s',
                                               client = path[0]))
