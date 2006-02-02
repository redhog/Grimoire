import Grimoire.About, Grimoire.Performer, Grimoire.Types


Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class about(Grimoire.Performer.Method):
        def _call(self):
            return Grimoire.About.abouts()
        def _params(self):
            return Ps()
