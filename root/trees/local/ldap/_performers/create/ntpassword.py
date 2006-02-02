import Grimoire.Performer, Grimoire.Types, sambapasswords

ntlmgenerator = sambapasswords.SmbPasswordGenerator()

class Performer(Grimoire.Performer.Base):
    class ntpassword(Grimoire.Performer.Method):
        __path__ = ['ntpassword', '$ldapservername']
        def _call(self, password):
            return (ntlmgenerator.LMPasswordHash(password),
                    ntlmgenerator.NTPasswordHash(password))
        def _params(self):
            return Grimoire.Types.AnnotatedValue(
                Grimoire.Types.ParamsType.derive(
                    [('password',
                      Grimoire.Types.AnnotatedValue(Grimoire.Types.NewPasswordType),
                      "Clear-text password to hash")]),
                "Create an LM and an NT password hash from a clear-text password")
