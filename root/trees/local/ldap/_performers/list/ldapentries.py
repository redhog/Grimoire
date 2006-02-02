import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, string, ldap, types

debugListings = 0

class Performer(Grimoire.Performer.Base):
    class ldapentries(Grimoire.Performer.SubMethod):
        __related_group__ = ['ldapentry']
        __path__ = ['ldapentries', '$ldapservername']
        def _call(self, path, depth = Grimoire.Performer.UnlimitedDepth,
                  filter = None, pathfilter = '(| (ou=*) (o=*))',
                  convertToDirList = True, stripTypes = True, lowerCaseify = True, addType = '', endType = '',
                  convertToLinks = False, linksReferer = None, linksBase = None):
            subDepth = depth
            if subDepth == -1:
                subDepth = Grimoire.Performer.UnlimitedDepth
            if subDepth < 0:
                return []
            elif subDepth < 1:
                scope = ldap.SCOPE_BASE
            elif subDepth < 2:
                scope = ldap.SCOPE_ONELEVEL
            else:
                scope = ldap.SCOPE_SUBTREE
            if addType:
                if (endType):
                    alternativePath = [ addType + '=' + part for part in path[:-1]] + [ endType + '=' + path[-1]]
                path = [addType + '=' + part for part in path]
            subPrefix = path
            conn = self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(['local', 'ldap', 'admin', 'conn'], cache=True))
            pathLen = len(string.join(path + [conn.realm], ','))
            baseDn = string.join(Grimoire.Utils.Reverse(subPrefix) + [conn.realm], ',')
            if linksReferer: linksReferer = Grimoire.Performer.Physical(linksReferer)
            if linksBase: linksBase = Grimoire.Performer.Physical(linksBase)
            def mangleDn(dn, leaf):
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
            res = []
            args = {'base': baseDn, 'scope': scope, 'attrlist': ['dn']}
            if filter:
                args['filterstr'] = filter
            if debugListings:
                print "LIST.LDAPENTRIES:", path, depth, args
            id = conn.search(**args)
            try:
                res += Grimoire.Utils.Map(lambda entry: mangleDn(entry[0], 1),
                                          conn.result(id)[1])[:]
            except ldap.NO_SUCH_OBJECT:
                if (endType):
                    # Make a new try with an alternative endtype
                    baseDn = string.join(Grimoire.Utils.Reverse(alternativePath) + [conn.realm], ',')
                    res = []
                    args = {'base': baseDn, 'scope': scope, 'attrlist': ['dn']}
                    if filter:
                        args['filterstr'] = filter
                    if debugListings:
                        print "LIST.LDAPENTRIES:", path, depth, args
                    id = conn.search(**args)
                    try:
                        res += Grimoire.Utils.Map(lambda entry: mangleDn(entry[0], 1),
                                          conn.result(id)[1])[:]
                    except ldap.NO_SUCH_OBJECT:
                        # Still no object: give up.
                        pass
            if (    filter
                and convertToDirList
                and (   scope == ldap.SCOPE_BASE
                     or scope == ldap.SCOPE_ONELEVEL)):
                if debugListings:
                    print "LIST.LDAPENTRIES: filter, convertToDirList", pathfilter
                del args['filterstr']
                if pathfilter:
                    args['filterstr'] = pathfilter
                id = conn.search(**args)
                try:
                    res += Grimoire.Utils.Map(lambda entry: mangleDn(entry[0], 0),
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
                     ],
                    0),
                Grimoire.Types.Formattable(
                    'List LDAP entries under %(path)s',
                    path=Grimoire.Utils.Reverse(path)))
