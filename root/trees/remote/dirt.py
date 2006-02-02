import Grimoire.Performer, Grimoire.Utils.Serialize.RPC, Grimoire.Types, Grimoire.Utils, string

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive


class Dirt(Grimoire.Performer.SubMethod):
    def _call(self, path, *arg, **kw):
        host = 'localhost'
        port = self._port
        if path:
            host = path[0]
            path = path[1:]
        if path and 0 not in map(lambda c: c in string.digits, path[0]):
            port = int(path[0])
            path = path[1:]
        if path:
            raise AttributeError('Spurious extra path elements after host and port')
            
        binding = self._callWithUnlockedTree(
            lambda: self._getpath(Grimoire.Types.MethodBase, 1).rpc.binding.dirt(*arg, **kw))

        client = self._callWithUnlockedTree(
            lambda: self._getpath(Grimoire.Types.MethodBase, 1).rpc.client(*arg, **kw))

        class ClientPerformerBinding(binding):
            def new(self, id):
                return client(binding.new(self, id))

        def ClientPerformerclient(*arg, **kw):
            return client(
                Grimoire.Utils.Serialize.RPC.BindingClient(
                    binding = ClientPerformerBinding,
                    *arg, **kw))
        
        res = ClientPerformerclient(
            self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 1,
                                      ['rpc', 'connect'] + self._transport
                                      )(host, port, *arg, **kw)))
        return Grimoire.Performer.Logical(res)
    def _dir(self, path, depth):
        return [(1, [])]

class Performer(Grimoire.Performer.Base):
    class ssl_dirt(Dirt):
        _port = Grimoire.Types.protocolMapping['ssl.dirt'][1]
        _transport = ['ssl']
        def _params(self, path):
            return A(Ps(),
                     'Connects to a remote host, specified by a path '
                     '(host, port), using '
                     'Grimoire-over-DIRT-over-SSL-over-tcp and returns '
                     'the remote tree as a locally accessible one')

    class dirt(Dirt):
        _port = Grimoire.Types.protocolMapping['dirt'][1]
        _transport = ['tcp']
        def _params(self, path):
            return A(Ps(),
                     'Connects to a remote host, specified by a path '
                     '(host, port), using Grimoire-over-DIRT-over-tcp '
                     'and returns the remote tree as a locally '
                     'accessible one')
