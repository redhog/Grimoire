import Grimoire.Utils, Grimoire.Performer, Grimoire.Types, ldap, string

defaultsParams = None
def getDefaultsParams(obj):
    global defaultsParams
    if not defaultsParams:
        defaultsParams = Grimoire.Types.getValue(
            getattr(obj.list.ldapattributes, '$ldapservername')(['grimoireDefaults'], [], ['objectClass', 'seeAlso', 'ou', 'l', 'cn'], 1))
    return defaultsParams

defaultsConvertingParams = None
def getDefaultsConvertingParams(obj):
    global defaultsConvertingParams
    if not defaultsConvertingParams:
        class ParamsType(getDefaultsParams(obj)):
            convertType = Grimoire.Types.convertParamsToUTF8
        defaultsConvertingParams = ParamsType
    return defaultsConvertingParams

class Performer(Grimoire.Performer.Base):
    class defaults(Grimoire.Performer.SubMethod):
        __path__ = ['defaults', '$ldapservername']
        def _call(self, path, *args, **kws):
            conn = self._callWithUnlockedTree(
                lambda:
                    self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                        ['local', 'ldap', 'admin', 'conn'], cache=True))
            dn = string.join(['cn=defaults'] + ['ou=' + item for item in Grimoire.Utils.Reverse(path)] + [conn.realm], ',')
            kws = self._callWithUnlockedTree(getDefaultsConvertingParams,
                                             self._getpath(Grimoire.Types.MethodBase, 1)).compileArgs(args, [], kws).kws
            try:
                conn.modify_s(dn, [(ldap.MOD_REPLACE, name, value) for (name, value) in kws.iteritems()])
            except ldap.NO_SUCH_OBJECT:
                kws['objectClass'] = 'grimoireDefaults'
                kws['cn'] = 'defaults'
                conn.add_s(dn, kws.items())
            return Grimoire.Types.AnnotatedValue(None,
                     'Successfully changed defaults')
        __dir_allowall__ = False        
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 1, ['list', 'ldapentries'] + ['$ldapservername'] + path)(
                    depth, 'ou=*', addType='ou'))
        def _params(self, path):
            conn = self._callWithUnlockedTree(
                lambda:
                    self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                        ['local', 'ldap', 'admin', 'conn'], cache=True))
            dn = string.join(['cn=defaults'] + ['ou=' + item for item in Grimoire.Utils.Reverse(path)] + [conn.realm], ',')
            params = self._callWithUnlockedTree(getDefaultsParams, self._getpath(Grimoire.Types.MethodBase, 1))
            defaults = {}
            id = conn.search(dn, ldap.SCOPE_BASE, attrlist = [name for (name, t) in params.arglist])
            try:
                defaults = conn.result(id)[1][0][1]
            except KeyError:
                pass
            except ldap.NO_SUCH_OBJECT:
                pass
            if defaults:
                params = params.addDefaults(defaults)
            return Grimoire.Types.AnnotatedValue(
                params,
                Grimoire.Types.Formattable(
                    'Change defaults for %(user)s',
                    user=Grimoire.Types.GrimoirePath(path)))
