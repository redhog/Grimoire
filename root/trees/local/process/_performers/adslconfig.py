import Grimoire, Grimoire.Utils, types, csv, os.path
from Grimoire.root.trees.local.process._performers._ppp import Peers

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class list_adsl_peers(Grimoire.Performer.SubMethod):
        __path__ = ['list', 'adsl', 'peers', '$processservername']
        __related_group__ = ['adsl', 'peer']
        def _call(self, path, depth, convertToDirList = True, onlyEnabled = False, onlyDisabled = False):
            if onlyEnabled or onlyDisabled :
                enabledProviders = set()
                out, err = Grimoire.Utils.system("ps", ("ps", "-o", "pid,cmd", "axw"), onlyOkStatus = True)
                # Output format is
                # 7668 /usr/sbin/pppd call dsl-provider
                # and we're basicly doing
                # ps -o pid,cmd axw | grep "pppd[ ]call" | sed -e "s+^.*call \(.*\)$+\1+g"
                for line in out.split('\n'):
                    if 'pppd call' in line:
                        enabledProviders.add(line.split(' call ')[1])

            if onlyEnabled:
                peers = enabledProviders
            else:
                peers = set(Peers.peers.peers.iterkeys())
                if onlyDisabled:
                    peers = peers - enabledProviders

            if convertToDirList:
                return Grimoire.Performer.DirListFilter(
                    path, depth,
                    [(1, [item]) for item in peers])
            else:
                peerdict = {}
                for key in peers:
                    peerdict[key] = Peers.peers.peers[key]
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
        def _call(self, name, client):
            Peers.peers.peers[name] = Peers.Peer(os.path.join(Peers.peers.path, name), True)
            Peers.peers.peers[name].properties['user'] = client
            Peers.peers.peers[name].save()
            return A(None,
                     'Peer successfully added')
        
        def _params(self):
            return A(Ps([('name', A(Grimoire.Types.NonemptyStringType,
                                    'Name of peer')),
                         ('client', A(Grimoire.Types.NonemptyStringType,
                                      'Client address (username@host)'))]),
                     'Add an ADSL peer')
        
    class delete_adsl_peer(Grimoire.Performer.SubMethod):
        __path__ = ['delete', 'adsl', 'peer', '$processservername']
        __related_group__ = ['adsl', 'peer']
        def _call(self, path):
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
            for key, value in Peers.peers.peers[path[0]].properties.items():
                if value is None:
                    if not arg[key]:
                        del Peers.peers.peers[path[0]].properties[key]
                else:
                    Peers.peers.peers[path[0]].properties[key] = arg[key]
            Peers.peers.peers[path[0]].save()
            return A(None,
                     'Peer successfully updated')
            
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase,
                                      path = ['list', 'adsl', 'peers', '$processservername'] + path
                                      )(depth))

        def _params(self, path):
            arglist = []
            for key, value in Peers.peers.peers[path[0]].properties.iteritems():
                if value is None:
                    arglist.append((key,
                                    A(Grimoire.Types.HintedType.derive(types.BooleanType, [True]),
                                      key)))
                else:
                    arglist.append((key,
                                    A(Grimoire.Types.HintedType.derive(types.StringType,
                                                                       [value]))))
            return A(Ps(arglist),
                     Grimoire.Types.Formattable('Change ADSL peer %(name)s',
                                                name = path[0]))
