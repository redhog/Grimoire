import Grimoire.Performer, Grimoire.Utils, Grimoire.Types
import string, ldap, types

class Performer(Grimoire.Performer.Base):
    class draftBySwedishIDNumber(Grimoire.Performer.SubMethod):
        __path__ = ['draftBySwedishIDNumber', '$ldapservername']
        def _call(self, path, **kw):
            if len(path) != 1:
                raise AttributeError()
            conn = self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                    ['local', 'ldap', 'admin', 'conn'], cache=True))
            id = conn.search('ou=People,ou=Drafts,' + conn.realm, ldap.SCOPE_SUBTREE, 'grimoireSwedishIDNumber=' + path[0], attrlist=['dn'])
            try:
                dn = conn.result(id)[1][0][0]
            except IndexError:
                raise KeyError(Grimoire.Types.Formattable(
                    'There is no user account draft with personal ID number %(grimoireSwedishIDNumber)s',
                    grimoireSwedishIDNumber=path[0]))
            if 'uid' in kw:
                id = conn.search(conn.realm,
                                 ldap.SCOPE_SUBTREE,
                                 'uid=' + Grimoire.Utils.encode(kw['uid'], 'ascii'),
                                 attrlist=['dn'])
                if len(conn.result(id)[1]) != 0:
                    raise Exception('The proposed username is already used by someone else. Please choose another one.')
            conn.modify_s(dn,
                          [(ldap.MOD_REPLACE, name, Grimoire.Utils.encode(value, 'ascii'))
                           for name, value in kw.iteritems()])
            id = conn.search(dn, ldap.SCOPE_BASE)
            res = conn.result(id)[1][0][1]
            return Grimoire.Types.AnnotatedValue(
                res,
                Grimoire.Types.Formattable(
                    '%(name)s successfully changed',
                    name=name)) # FIXME: This is unbound here, shouldn't this be something like path[0]?
        __dir_allowall__ = False
        def _dir(self, path, depth):
            conn = self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                    ['local', 'ldap', 'admin', 'conn'], cache=True))
            id = conn.search('ou=People,ou=Drafts,' + conn.realm,
                             ldap.SCOPE_SUBTREE,
                             '(& (objectClass=grimoireDraftAccount) (grimoireSwedishIDNumber=*))',
                             attrlist=['grimoireSwedishIDNumber'])
            return [(1, [post[1]['grimoireSwedishIDNumber'][0]]) for post in conn.result(id)[1]]
        def _params(self, path):
            return Grimoire.Types.AnnotatedValue(
                Grimoire.Types.ParamsType.derive(
                    [], 0, None,
                    Grimoire.Types.AnnotatedValue(
                          types.StringType,
                          "Values to set")),
                Grimoire.Types.Formattable(
                    'Change an attribute on draft %(path)s',
                    path=Grimoire.Types.GrimoirePath(path)))
