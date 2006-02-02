import Grimoire.Utils, Grimoire.Performer, Grimoire.Types, ldap, string

class Performer(Grimoire.Performer.Base):
    class ldapentry(Grimoire.Performer.SubMethod):
        __path__ = ['ldapentry', '$ldapservername']
        def _call(self, path, *args, **kws):
            conn = self._callWithUnlockedTree(
                lambda:
                    self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                        ['local', 'ldap', 'admin', 'conn'], cache=True))
            dn = string.join(Grimoire.Utils.Reverse(path) + [conn.realm], ',')

            """excludeArgs is intended for other methods that
            implements chaning specific types of entries with specific
            restrictions on which arguments are changeable."""

            excludeArgs = []
            if 'excludeArgs' in kws:
                excludeArgs = kws['excludeArgs']
                del kws['excludeArgs']

            class ParamsType(Grimoire.Types.getValue(self._params(path))):
                convertType = Grimoire.Types.convertParamsToUTF8
            ParamsType = ParamsType.removeArgs(*excludeArgs)

            kws = ParamsType.compileArgs(args, [], kws).kws

            deleteargs=[]
            for (name, type) in ParamsType.arglist:
                if name not in kws:
                    deleteargs.append(name)
            
            conn.modify_s(dn,
                          [(ldap.MOD_REPLACE, name, value) for (name, value) in kws.iteritems()]
                          + [(ldap.MOD_REPLACE, name, ()) for name in deleteargs])
            return Grimoire.Types.AnnotatedValue(None,
                     'Successfully changed entry')

        __dir_allowall__ = False #- setting this leads to recursion depth problems
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 1,
                                      ['list', 'ldapentries', '$ldapservername'] + path
                                      )(depth, stripTypes = 0))

        def _params(self, path):
            params = self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 1,
                                      ['list', 'ldapattributes', 'ofentry', '$ldapservername'] + path)())
            comment = Grimoire.Types.getComment(params)
            params = Grimoire.Types.getValue(params).removeArgs('objectClass', Grimoire.Types.LosePasswordType)
            class params(params):
                required=0
            return Grimoire.Types.AnnotatedValue(
                params,
                Grimoire.Types.Lines(
                    Grimoire.Types.Formattable("Change %(path)s", path=Grimoire.Types.GrimoirePath(path)),
                    comment))
