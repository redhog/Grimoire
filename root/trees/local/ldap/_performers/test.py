import Grimoire.Performer, Grimoire.Types, types

class Performer(Grimoire.Performer.Base):
    class test_fancy(Grimoire.Performer.Method):
        __path__ = ['test', 'fancy', '$ldapservername']
        def _call(self, foo, bar, fie=None):
            return Grimoire.Types.AnnotatedValue(
                'Foo: ' + unicode(foo) + ', Bar: ' + unicode(bar) + ', Fie: ' + unicode(fie),
                Grimoire.Types.Formattable(
                    'The testfunction (with e-mail adress %(address)s and link %(link)s) was called with the following arguments',
                    address=Grimoire.Types.EMailAddress(
                        'username',
                        Grimoire.Types.DNSDomain(['se', 'takeit', 'lab', 'testmachine'])),
                    link=Grimoire.Types.TitledURILink(Grimoire.Types.GrimoireReference(2, ['create', 'user', 'administrators']),
                                                      'create user')))

        def _params(self):
            return Grimoire.Types.AnnotatedValue(\
                Grimoire.Types.ParamsType.derive(\
                    [('foo',
                      Grimoire.Types.AnnotatedValue(\
                          Grimoire.Types.HintedType.derive(Grimoire.Types.NewPasswordType,
                                                    ['Baziiko', 'Filifjonka']),
                          "New password to set")),
                     ('bar',
                      Grimoire.Types.AnnotatedValue(\
                          Grimoire.Types.HintedType.derive(Grimoire.Types.NonemptyStringType,
                                                    ["foo", "bar"]),
                          "Roligt ord")),
                     ('fie',
                      Grimoire.Types.AnnotatedValue(\
                          Grimoire.Types.RestrictedType.derive(types.StringType,
                                                        ["hej", "gu", "gxxx"]),
                          "Blabla")),
                     ],
                    2),
                'This is a test of the system. This method will just return a dummy string based on its input')

    class test_err(Grimoire.Performer.Method):
        __path__ = ['test', 'err', '$ldapservername']
        def _call(self, foo):
            pass

        def _params(self):
            raise AttributeError('And the gnome said that x < y and that is why.')

    class test_simple(Grimoire.Performer.Method):
        __path__ = ['test', 'simple', '$ldapservername']
        def _call(self, *arg, **kw):
            return (arg, kw)
        def _params(self):
            return Grimoire.Types.ParamsType.derive()
