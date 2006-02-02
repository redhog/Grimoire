"""This module implements abilities, such as the ones defined in the
Ability module, that takes their set of allowed path from an LDAP
database."""

import Grimoire.Types.Ability, Grimoire.Utils, ldap, string

class AttrsList(Grimoire.Types.Ability.List):
    """This ability list takes its set of allows, denies and ignores
    from one or more LDAP entry attribute listing. Abilities to allow
    are taken from the attribute AbilityAllow, the ones to deny from
    AbilityDeny and the ones to ignore are taken from the attribute
    AbilityIgnore. In these attributes, the paths are represented as
    strings separated by a dot (.)

    The paths are sorted on their lengths with the longest ones first.
    """
    def fromLDAPAttrs(cls, *attrss):
        rights = []
        for attrs in attrss:
            try:
                try:
                    allows = attrs['grimoireAbilityAllow']
                except KeyError:
                    allows = []
                try:
                    denies = attrs['grimoireAbilityDeny']
                except KeyError:
                    denies = []
                try:
                    ignores = attrs['grimoireAbilityIgnore']
                except KeyError:
                    ignores = []
                attrrsights = ([(Grimoire.Types.Ability.Allow, path[1:].split('.')) for path in allows] +
                               [(Grimoire.Types.Ability.Deny, path[1:].split('.')) for path in denies] +
                               [(Grimoire.Types.Ability.Ignore, path[1:].split('.')) for path in ignores])
                attrrsights.sort(lambda x, y: len(y[1]) - len(x[1]))
                rights.extend(attrrsights)
            except IndexError:
                pass
        return cls(rights)
    fromLDAPAttrs = classmethod(fromLDAPAttrs)

    def toLDAPAttrs(self):
        def filter(what):
            def filter((c, s)):
                if c is not what:
                    raise Grimoire.Utils.FilterOutError()
                return Grimoire.Utils.encode('.' + s.path, 'utf-8')
            return filter
        allows = tuple(Grimoire.Utils.Map(filter(Grimoire.Types.Ability.Allow), self.abilities))
        denies = tuple(Grimoire.Utils.Map(filter(Grimoire.Types.Ability.Deny), self.abilities))
        ignores = tuple(Grimoire.Utils.Map(filter(Grimoire.Types.Ability.Ignore), self.abilities))
        attrs = {}
        if allows:
            attrs['grimoireAbilityAllow'] = allows
        if denies:
            attrs['grimoireAbilityDeny'] = denies
        if ignores:
            attrs['grimoireAbilityIgnore'] = ignores
        return attrs

class EntriesList(AttrsList):
    """This AttrsList takes its set of entry attribute lists from the
    LDAP entries specified by a set of DNs.
    """
    def fromLDAPEntries(cls, conn, *dns):
        attrss = []
        for dn in dns:
            try:
                attrss.append(conn.search_s(dn + ',' + conn.realm, ldap.SCOPE_BASE,
                                            attrlist=['grimoireAbilityAllow', 'grimoireAbilityDeny', 'grimoireAbilityIgnore'])[0][1])
            except (IndexError, ldap.NO_SUCH_OBJECT):
                pass
        return cls.fromLDAPAttrs(*attrss)
    fromLDAPEntries = classmethod(fromLDAPEntries)

    def toLDAPEntry(self, conn, dn):
        attrs = self.toLDAPAttrs()
        dn = Grimoire.Utils.encode(dn + ',' + conn.realm, 'utf-8')
        try:
            conn.modify_s(dn, [(ldap.MOD_REPLACE, name, value) for (name, value) in attrs.iteritems()])
        except ldap.NO_SUCH_OBJECT:
            attrs['objectClass'] = 'grimoireAbilityList'
            type, name = dn.split(',', 1)[0].split('=', 1)
            attrs[type] = name
            conn.add_s(dn, attrs.items())

def homeGroupMemberships(conn, dn):
    """Returns a list of DNs of home-groups of a user, sorted by thir
    length, with the longest ones first.
    """
    groupdns =[]
    for prefix in Grimoire.Utils.Prefixes(Grimoire.Utils.Reverse(dn.split(',')))[1:]:
        groupdns += [string.join(Grimoire.Utils.Reverse(prefix), ',')]
    return groupdns

def groupMemberships(conn, dn):
    """Returns a list of DNs of groups a user is a member of
    (memberUid=username), sorted by thir length, with the longest ones
    first.
    """
    groupdns =[]
    uid = dn.split(',')[0].split('=')[1]
    id = conn.search(conn.realm, ldap.SCOPE_SUBTREE, "memberUid=%s" % uid, attrlist = ['dn'])
    try:
        dns =  conn.result(id)[1]
        groupdns.extend(map(lambda x: x[0][:-len(conn.realm)-1], dns))
    except ldap.NO_SUCH_OBJECT:
        pass
    groupdns.sort(lambda x, y: len(y.split(',')) - len(x.split(',')))
    return groupdns

def ownedGroups(conn, dn):
    groupdns =[]
    id = conn.search(conn.realm, ldap.SCOPE_SUBTREE, "owner=%s" % dn, attrlist = ['dn'])
    try:
        dns =  conn.result(id)[1]
        groupdns.extend(map(lambda x: x[0][:-len(conn.realm)-1], dns))
    except ldap.NO_SUCH_OBJECT:
        pass
    groupdns.sort(lambda x, y: len(y.split(',')) - len(x.split(',')))
    return groupdns

class UserList(EntriesList):
    """This ability is a EntriesList with the set of entries being the
    ones named cn=security under

    1. the users own entry,

    2. under the home-group and any surrounding group (=groups having
       a suffix of the home-group-DN as DN), sorted on the length of
       the DN, with the longest ones first,

    3. and under each group the user is a member of (that is, the ones
       that has a memberUid=username-attribute), sorted on the length
       of their DNs, with the longest ones first.
    """
    def fromUser(cls, conn, dn, onlyTransferable = False):
        groups = [dn]
        if onlyTransferable:
            groups += ownedGroups(conn, dn)
        else:
            groups += homeGroupMemberships(conn, dn) + groupMemberships(conn, dn)
        return cls.fromLDAPEntries(
            conn,
            *['cn=security' + ['', ','][group != ''] + group
              for group in groups])
    fromUser = classmethod(fromUser)

    def toUserOrGroup(self, conn, dn):
        self.toLDAPEntry(conn, 'cn=security' + ['', ','][dn != ''] + dn)

class LdapAbility(Grimoire.Types.Ability.CachedAbility):
    """Base-class for all caching LDAP-based ability-classes."""
    def __init__(self, dn, conn):
        """conn is an LDAP-connection, and dn is the distinguished
        name (DN) of the user-object in LDAP of the current user.
        """
        self.dn = dn
        self.conn = conn
        # Check that conn does have a conn.realm
        foo = conn.realm
        Grimoire.Types.Ability.CachedAbility.__init__(self)

class LdapEntryList(LdapAbility):
    def genAbility(self):
        return EntriesList.fromLDAPEntries(self.conn, self.dn)

class LdapList(LdapAbility):
    def genAbility(self):
        return UserList.fromUser(self.conn, self.dn)
