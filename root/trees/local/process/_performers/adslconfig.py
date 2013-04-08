import Grimoire, Grimoire.Utils, types, csv, os.path
from Grimoire.root.trees.local.process._performers._ppp import Peers
from Grimoire.root.trees.local.process._performers._ppp import ChapSecrets

pls = os.path.join(os.path.split(__file__)[0], '_ppp/pls')

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive
H = Grimoire.Types.HintedType.derive

class Performer(Grimoire.Performer.Base):
    class list_adsl_peers(Grimoire.Performer.SubMethod):
        __path__ = ['list', 'adsl', 'peers', '$processservername']
        __related_group__ = ['adsl', 'peer']
        def _call(self, path, depth, convertToDirList = True, onlyEnabled = False, onlyDisabled = False):
            if onlyEnabled or onlyDisabled or not convertToDirList:
                enabledProviders = {}
                out, err = Grimoire.Utils.system(pls, (pls,), onlyOkStatus = True)
                # Output format is
                #
                # pid   if   local ip     remote ip      netmask         peer-name
                # 28464 ppp1 192.168.10.1 192.168.10.221 255.255.255.255 dsl-provider

                for line in out.split('\n'):
                    line = line.split(',')
                    if len(line) < 6: continue
                    enabledProviders[line[5]] = {'pid': line[0],
                                                 'if':  line[1],
                                                 'local': line[2],
                                                 'remote': line[3],
                                                 'netmask': line[4]
                                                 }

            if onlyEnabled:
                peers = set(enabledProviders.iterkeys())
            else:
                peers = set(Peers.peers.peers.iterkeys())
                if onlyDisabled:
                    peers = peers - set(enabledProviders.iterkeys())

            if convertToDirList:
                return Grimoire.Performer.DirListFilter(
                    path, depth,
                    [(1, [item]) for item in peers])
            else:
                peerdict = {}
                for key in peers:
                    peerdict[key] = Peers.peers.peers[key]
                    peerdict[key].connection = None
                    if key in enabledProviders:
                        peerdict[key].connection = enabledProviders[key]
                return peerdict

        def _dir(self, path, depth):
            return self._call(path, depth)

        def _params(self, path):
            return A(Ps([('depth',
                          A(types.IntType,
                            "Only return entries this far down in the tree (-1 means infinity)")),
                         ('convertToDirList',
                          A(Grimoire.Types.BooleanType,
                            "Convert entry listing to a Grimoire directory listing")),]),
                     'List adsl accounts')

    class create_adsl_peer(Grimoire.Performer.Method):
        __path__ = ['create', 'adsl', 'peer', '$processservername']
        __related_group__ = ['adsl', 'peer']
        def _call(self, name, client, secret, ip):
            if '*' not in ChapSecrets.chapSecrets.items:
                ChapSecrets.chapSecrets.items['*'] = {}
            ChapSecrets.chapSecrets.items['*'][client] = {'server': '*', 'client': client, 'secret': secret, 'ip': ip}
            ChapSecrets.chapSecrets.save()
            Peers.peers.peers[name] = Peers.Peer(os.path.join(Peers.peers.path, name), True)
            Peers.peers.peers[name].properties['user'] = client
            Peers.peers.peers[name].save()
            return A(None,
                     'Peer successfully added')
        
        def _params(self):
            return A(Ps([('name', A(Grimoire.Types.NonemptyStringType,
                                    'Name of peer')),
                         ('client', A(Grimoire.Types.NonemptyStringType,
                                      'Client address (username@host)')),
                         ('secret', A(Grimoire.Types.NewPasswordType,
                                      'Passphrase')),
                         ('ip', A(types.StringType,
                                  'IP address of remote machine'))]),
                     'Add an ADSL peer')
        
    class delete_adsl_peer(Grimoire.Performer.SubMethod):
        __path__ = ['delete', 'adsl', 'peer', '$processservername']
        __related_group__ = ['adsl', 'peer']
        def _call(self, path):
            if (    'user' in Peers.peers.peers[path[0]].properties
                and '*' in ChapSecrets.chapSecrets.items
                and Peers.peers.peers[path[0]].properties['user'] in ChapSecrets.chapSecrets.items['*']):
                del ChapSecrets.chapSecrets.items['*'][Peers.peers.peers[path[0]].properties['user']]
                ChapSecrets.chapSecrets.save()
            del Peers.peers.peers[path[0]]
            Peers.peers.save()
            return A(None,
                     'Peer successfully deleted')
            
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase,
                                      path = ['list', 'adsl', 'peers', '$processservername'] + path
                                      )(depth))

        def _params(self, path):
            return A(Ps([]),
                     'Delete ADSL peer')

    class change_adsl_peer_properties(Grimoire.Performer.SubMethod):
        __path__ = ['change', 'adsl', 'peer', 'properties', '$processservername']
        __related_group__ = ['adsl', 'peer']
        def _call(self, path, **arg):
            if '*' not in ChapSecrets.chapSecrets.items:
                ChapSecrets.chapSecrets.items['*'] = {}
            if arg['user'] in ChapSecrets.chapSecrets.items['*']:
                ChapSecrets.chapSecrets.items['*'][arg['user']]['secret'] = arg['secret']
                ChapSecrets.chapSecrets.items['*'][arg['user']]['ip'] = arg['ip']
            else:
                ChapSecrets.chapSecrets.items['*'][arg['user']] = {'server': '*', 'client': arg['user'], 'secret': arg['secret'], 'ip': arg['ip']}
            ChapSecrets.chapSecrets.save()
            del arg['secret']
            del arg['ip']
            Peers.peers.peers[path[0]].properties.update(arg)
            Peers.peers.peers[path[0]].save()
            return A(None,
                     'Peer successfully updated')
            
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase,
                                      path = ['list', 'adsl', 'peers', '$processservername'] + path
                                      )(depth))

        def _params(self, path):
            secret = ''
            ip = ''
            user = ''
            if (    'user' in Peers.peers.peers[path[0]].properties
                and '*' in ChapSecrets.chapSecrets.items
                and Peers.peers.peers[path[0]].properties['user'] in ChapSecrets.chapSecrets.items['*']):
                user = Peers.peers.peers[path[0]].properties['user']
                secret = ChapSecrets.chapSecrets.items['*'][user]['secret']
                ip = ChapSecrets.chapSecrets.items['*'][user]['ip']
            arglist = [('user', A(H(Grimoire.Types.NonemptyStringType, [user]),
                                  'User (username@host)')),
                       ('secret', A(H(Grimoire.Types.NewPasswordType, [secret]),
                                    'Passphrase')),
                       ('ip', A(H(types.StringType, [ip]),
                                'IP address of remote machine'))]
            for key, value in Peers.peers.peers[path[0]].properties.iteritems():
                if value is not None:
                    arglist.append((key,
                                    A(H(types.StringType,
                                        [value]),
                                      key)))
            return A(Ps(arglist),
                     Grimoire.Types.Formattable('Change ADSL peer %(name)s',
                                                name = path[0]))
