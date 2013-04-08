import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, string, ldap, types

debugListings = 0

class Performer(Grimoire.Performer.Base):
    #### fixme ####
    # description = """This is probably the worst cruft in all of
    # Grimoire - it's only here because LDAP stores paths
    # _with_types_, like
    # mail=nana@hehe,ou=foo,dc=bar,cn=gazonk,dc=org, not just
    # nana@hehe,foo,bar,gazonk,org, which is what we'd like to show
    # the user. The solution is of course to allow AnnotatedValues in
    # paths, but that would require quite some hacking on the GUI
    # code, and probably other places aswell, and would probably be
    # slow as hell. So till that is fixed, we're left with this bloody
    # magic."""
    #### end ####
    class ldapentries(Grimoire.Performer.SubMethod):
        __related_group__ = ['ldapentry']
        __path__ = ['ldapentries', '$ldapservername']
        def _call(self, path, depth = Grimoire.Performer.UnlimitedDepth,
                  filter = "(objectClass=*)", pathfilter = '(| (ou=*) (o=*))',
                  convertToDirList = True, stripTypes = True, lowerCaseify = True, addType = '', beginType = '', endType = '',
                  convertToLinks = False, linksReferer = None, linksBase = None):
            subDepth = depth
            if subDepth == -1:
                subDepth = Grimoire.Performer.UnlimitedDepth
            if subDepth < 0:
                return []
            elif subDepth < 1:
                scopes = [ldap.SCOPE_BASE]
            elif subDepth < 2:
                scopes = [ldap.SCOPE_BASE, ldap.SCOPE_ONELEVEL]
            else:
                scopes = [ldap.SCOPE_SUBTREE]
            alternativePath = None
            if addType:
                if endType:
                    if beginType:
                        alternativePath = [beginType + '=' + path[0]] + [addType + '=' + part for part in path[1:-1]] + [endType + '=' + path[-1]]
                    else:
                        alternativePath = [addType + '=' + part for part in path[:-1]] + [endType + '=' + path[-1]]
                if beginType:
                    path = [beginType + '=' + path[0]] + [addType + '=' + part for part in path[1:]]
                else:
                    path = [addType + '=' + part for part in path]
            conn = self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(['local', 'ldap', 'admin', 'conn'], cache=True))
            if linksReferer: linksReferer = Grimoire.Performer.Physical(linksReferer)
            if linksBase: linksBase = Grimoire.Performer.Physical(linksBase)
            def mangleDn(dn, pathLen, leaf):
                if lowerCaseify:
                    dn = dn.lower()
                reslen = len(dn) - pathLen
                if reslen:
                    reslen -= 1 # remove the ,-sign separating base from the rest too
                dn = dn[:reslen]
                if not convertToDirList and not convertToLinks:
                    return dn
                def manglePair(pair):
                    if stripTypes and pair:
                        pair = pair.split('=')[1]
                    return pair
                if dn:
                    dn = dn.split(',')
                    dn.reverse()
                else:
                    dn = []
                dn = map(manglePair, dn)
                if convertToDirList:
                    return (leaf, dn)
                elif convertToLinks:
                    return Grimoire.Types.TitledURILink(linksReferer._reference(linksBase._getpath(path=dn)),
                                                        Grimoire.Types.GrimoirePath(dn))
            baseDn = string.join(Grimoire.Utils.Reverse(path) + [conn.realm], ',')        
            searches = [({'scope': scope, 'filterstr': filter, 'attrlist': ['dn'], 'base': baseDn}, len(baseDn), 1) for scope in scopes]
            if alternativePath is not None:
                alternativeDn = string.join(Grimoire.Utils.Reverse(alternativePath) + [conn.realm], ',')
                searches += [({'scope': scope, 'filterstr': filter, 'attrlist': ['dn'], 'base': alternativeDn}, len(alternativeDn), 1) for scope in scopes]
            if (    filter != "(objectClass=*)"
                and convertToDirList
                and (   scope == ldap.SCOPE_BASE
                     or scope == ldap.SCOPE_ONELEVEL)):
                searches += [({'scope': scope, 'filterstr': pathfilter, 'attrlist': ['dn'], 'base': baseDn}, len(baseDn), 0) for scope in scopes]
            res = []
            for args, pathLen, leaf in searches:
                id = conn.search(**args)
                try:
                    res += Grimoire.Utils.Map(lambda entry: mangleDn(entry[0], pathLen, leaf),
                                              conn.result(id)[1])[:]
                except ldap.NO_SUCH_OBJECT:
                    pass
            if convertToLinks:
                res = Grimoire.Types.Lines(*res)
            return res

        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath()(depth, None, None, stripTypes=False))
        def _params(self, path):
            return Grimoire.Types.AnnotatedValue(
                Grimoire.Types.ParamsType.derive(
                    [('depth',
                      Grimoire.Types.AnnotatedValue(
                          types.IntType,
                          "Only return entries this far down in the tree (-1 means infinity)")),
                     ('filter',
                      Grimoire.Types.AnnotatedValue(
                          types.StringType,
                          "LDAP search filter")),
                     ('pathfilter',
                      Grimoire.Types.AnnotatedValue(
                          types.StringType,
                          "LDAP search filter for items along a path to the desired items (Only used when convertToDirList is true, and depth is too small, to include all needed non-leaf-paths)")),
                     ('convertToDirList',
                      Grimoire.Types.AnnotatedValue(
                          Grimoire.Types.BooleanType,
                          "Convert entry listing to a Grimoire directory listing (that is, reverse and split DNs at ',')")),
                     ('stripTypes',
                      Grimoire.Types.AnnotatedValue(
                          Grimoire.Types.BooleanType,
                          "Remove leading type= from each part of the Grimoire paths")),
                     ('lowerCaseify',
                      Grimoire.Types.AnnotatedValue(
                          Grimoire.Types.BooleanType,
                          "Lower the case of all DNs")),
                     ('addType',
                      Grimoire.Types.AnnotatedValue(
                          types.StringType,
                          "Add this type to items in path (empty means items are typed already)")),
                     ('beginType',
                      Grimoire.Types.AnnotatedValue(
                          types.StringType,
                          "Add this type to the first item in path (empty means same as addType)")),
                     ('endType',
                      Grimoire.Types.AnnotatedValue(
                          types.StringType,
                          "Add this type to items (the final element of a path) (empty means same as addType)")),
                     ],
                    0),
                Grimoire.Types.Formattable(
                    'List LDAP entries under %(path)s',
                    path=Grimoire.Utils.Reverse(path)))
