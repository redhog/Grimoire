import Grimoire.Performer, Grimoire.Types, socket, types

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class tcp(Grimoire.Performer.Method):
        def _call(self, *arg, **kw):
            return socket.socket()
        def _params(self, path):
            return A(Ps(),
                     'Sets up a tcp socket')
