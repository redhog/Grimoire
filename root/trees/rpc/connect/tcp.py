import Grimoire.Performer, types, socket

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class tcp(Grimoire.Performer.Method):
        def _call(self, host, port, *arg, **kw):
            sock = socket.socket()
            sock.connect((host, port))
            sock.setblocking(1)
            return sock
        def _params(self):
            return A(Ps([('host', A(types.StringType,
                                    'Name of host to connect to')),
                         ('port', A(types.IntType,
                                    'Port to connect to'))]),
                     'Connects to a remote host, specified by a host and a '
                     'port using TCP/IP')
