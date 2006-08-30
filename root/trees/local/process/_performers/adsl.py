import Grimoire, Grimoire.Utils, types, csv, os.path
from Grimoire.root.trees.local.process._performers._ppp import Peers

poff = os.path.join(os.path.split(__file__)[0], '_ppp/poff')

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class enable_adsl_peer(Grimoire.Performer.SubMethod):
        __path__ = ['enable', 'adsl', 'peer', '$processservername']
        __related_group__ = ['adsl', 'peer']
        def _call(self, path):
            out, err = Grimoire.Utils.system("pon", ("pon", path[0]), onlyOkStatus = True)
            return out
            
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase,
                                      path = ['list', 'adsl', 'peers', '$processservername'] + path
                                      )(depth, onlyDisabled = True))

        def _params(self, path):
            return A(Ps([]),
                     'Enable ADSL connection to peer')

    class disable_adsl_peer(Grimoire.Performer.SubMethod):
        __path__ = ['disable', 'adsl', 'peer', '$processservername']
        __related_group__ = ['adsl', 'peer']
        def _call(self, path):
            out, err = Grimoire.Utils.system(poff, (poff, path[0]), onlyOkStatus = True)
            return out
            
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase,
                                      path = ['list', 'adsl', 'peers', '$processservername'] + path
                                      )(depth, onlyEnabled = True))

        def _params(self, path):
            return A(Ps([]),
                     'Disable ADSL connection to peer')
