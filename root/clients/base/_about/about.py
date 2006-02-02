import Grimoire.Performer, Grimoire.Types

class Performer(Grimoire.Performer.Base):
    class about(Grimoire.Performer.Method):
        def _call(self):
            return Grimoire.Types.AnnotatedValue(Grimoire.Types.Reducible(Grimoire.About.abouts(), '\n'),
                                                 'About Grimoire')
        def _params(self):
            return Grimoire.Types.ParamsType.derive()

