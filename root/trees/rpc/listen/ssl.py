import Grimoire.Performer, Grimoire.Types, types

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class ssl(Grimoire.Performer.Method):
        def _call(self, *arg, **kw):
            import Grimoire.Utils.M2fixed, M2Crypto
            if 'ssl_context' in kw:
                ctx = kw['ssl_context']
            else:
                ctx = M2Crypto.SSL.Context()
                try:
                    params = self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters
                    if 'cacert' in kw:
                        cacert = kw['cacert']
                    else:
                        cacert = params(['server', 'ssl', 'cert'])
                    if 'caprivkey' in kw:
                        caprivkey = kw['caprivkey']
                    else:
                        caprivkey = params(['server', 'ssl', 'privkey'])
                    ctx.load_cert(cacert, caprivkey)
                except (AttributeError, TypeError):
                    pass
            return Grimoire.Utils.M2fixed.Connection(ctx)
        def _params(self, path):
            return A(Ps([('cacert', A(types.UnicodeType,
                                    'Path to CA-certificate to use to authenticate oneself')),
                         ('caprivkey', A(types.UnicodeType,
                                    'Private key of CA-certificate to use to authenticate oneself'))],
                        0),
                     'Sets up an ssl socket')
