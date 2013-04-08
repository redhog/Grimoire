import Grimoire.Performer, types

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class ssl(Grimoire.Performer.Method):
        def _call(self, host, port, cacert = None, ssl_context = None, *arg, **kw):
            import Grimoire.Utils.M2fixed, M2Crypto
            if ssl_context:
                ctx = ssl_context
            else:
                ctx = M2Crypto.SSL.Context()
                try:
                    cacert = cacert or self._callWithUnlockedTree(
                        lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                            ['remote', 'ssl', 'cacert']))
                    ctx.load_verify_info(cacert)
                    ctx.set_verify(M2Crypto.SSL.verify_peer, 10)
                except (AttributeError, TypeError):
                    pass
            sock = Grimoire.Utils.M2fixed.Connection(ctx)
            sock.connect((host, port))
            sock.setblocking(1)
            return sock
        def _params(self):
            return A(Ps([('host', A(types.StringType,
                                    'Name of host to connect to')),
                         ('port', A(types.IntType,
                                    'Port to connect to')),
                         ('cacert', A(types.UnicodeType,
                                      'Path to CA-certificate to verify server end with'))]),
                     'Connects to a remote host, specified by a host and a '
                     'port using SSL over TCP/IP')
