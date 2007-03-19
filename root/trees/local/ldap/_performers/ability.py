import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, Grimoire.root.trees.local.ldap._Ability, types, ldap, string, thread

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

SM = Grimoire.Performer.SubMethod

class AllowMethod:
    def _params(self, path):
        return A(Ps([('filter', A(Grimoire.Types.Ability.List,
                                  'Abilities you wish to grant'))]),
                 Grimoire.Types.Formattable(
                     'Grant some of your own (transferable) abilities to %(path)s',
                     path=self._pathType(path)))
AM = AllowMethod

class CancelAllowMethod:
    def _params(self, path):
        return A(Ps([('filter', A(Grimoire.Types.Ability.List,
                                  'Abilities you wish to cancel'))]),
                 Grimoire.Types.Formattable(
                     "Cancel some of %(path)s's abilities",
                     path=self._pathType(path)))
CAM = CancelAllowMethod

class DenyMethod:
    def _params(self, path):
        return A(Ps([('filter', A(Grimoire.Types.Ability.List,
                                  'Abilities you wish to deny'))]),
                 Grimoire.Types.Formattable(
                     'Deny %(path)s some abilities',
                     path=self._pathType(path)))
DM = DenyMethod

class CancelDenyMethod:
    def _params(self, path):
        return A(Ps([('filter', A(Grimoire.Types.Ability.List,
                                  'Denials you wish to cancel'))]),
                 Grimoire.Types.Formattable(
                     'Deny %(path)s some abilities',
                     path=self._pathType(path)))
CDM = CancelDenyMethod

class SetMethod:
    def _params(self, path):
        return A(Ps([('ability', A(Grimoire.Types.Ability.List,
                                  'Abilities you to grant'))]),
                 Grimoire.Types.Formattable(
                     'Set some abilities for %(path)s',
                     path=self._pathType(path)))
SEM = SetMethod

class UnSetMethod:
    def _params(self, path):
        return A(Ps([('ability', A(Grimoire.Types.Ability.List,
                                  'Abilities you to grant'))]),
                 Grimoire.Types.Formattable(
                     'Unset some abilities for %(path)s',
                     path=self._pathType(path)))
USEM = UnSetMethod

class DNMethod:
    _pathType = Grimoire.Types.DN
    def _dir(self, path, depth):
        return self._callWithUnlockedTree(
            lambda:
                self._getpath(Grimoire.Types.MethodBase, path=['list', 'ldapentries', '$ldapservername'] + path)(
                    depth,
                    '(| (objectClass=posixAccount) (ou=*))',
                    stripTypes=True))
DNM = DNMethod

class UserMethod:
    _pathType = Grimoire.Types.GrimoirePath
    def _call(self, path, *arg, **kw):
        return self._callWithUnlockedTree(
            lambda:
                self._getpath(levels=1,
                              path=['dn', '$ldapservername', 'ou=people'] +
                              ['ou=' + name
                               for name in path[:-1]] +
                              ['uid=' + path[-1]])(*arg, **kw))
    def _dir(self, path, depth):
        return self._callWithUnlockedTree(
            lambda:
                self._getpath(Grimoire.Types.MethodBase,
                              path=['list', 'ldapentries', '$ldapservername', 'ou=people'] + path)(
                    depth + 1,
                    'objectClass=posixAccount',
                    addType='ou', endType='uid'))
UM = UserMethod

class GroupMethod:
    _pathType = Grimoire.Types.GrimoirePath
    def _call(self, path, *arg, **kw):
        return self._callWithUnlockedTree(
            lambda:
                self._getpath(levels=1,
                              path=['dn', '$ldapservername'] +
                              ['ou=' + name
                               for name in path])(*arg, **kw))
    def _dir(self, path, depth):
        return self._callWithUnlockedTree(
            lambda:
                self._getpath(Grimoire.Types.MethodBase, path=['list', 'ldapentries', '$ldapservername'] + path)(
                    depth,
                    'ou=*',
                    addType='ou'))
GM = GroupMethod

abilityLock = thread.allocate_lock()

class Performer(Grimoire.Performer.Base):
    class change_ability_allow_dn(DNM, AM, SM):
        __path__ = ['change', 'ability', 'allow', 'dn', '$ldapservername']
        _pathType = Grimoire.Types.DN
        def _call(self, path, filter):
            conn = self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                    ['local', 'ldap', 'admin', 'conn'], cache=True))
            userdn = self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                    ['local', 'ldap', 'user', 'dn']))
            dn = unicode(Grimoire.Types.DN(path + ['cn=security']))
            abilityLock.acquire()
            try:
                Grimoire.root.trees.local.ldap._Ability.EntriesList.fromLDAPEntries(conn, dn).allow(
                    Grimoire.root.trees.local.ldap._Ability.UserList.fromUser(conn, userdn, True),
                    filter
                    ).toLDAPEntry(conn, dn)
            finally:
                abilityLock.release()
            return A(None,
                     'Successfully allowed access')
        
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda:
                    self._getpath(Grimoire.Types.MethodBase, path=['list', 'ldapentries', '$ldapservername'] + path)(
                        depth,
                        '(| (objectClass=posixAccount) (ou=*))',
                        stripTypes=False))
        
        def _params(self, path):
            conn = self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                    ['local', 'ldap', 'admin', 'conn'], cache=True))
            dn = unicode(Grimoire.Types.DN(path + ['cn=security']))
            current = Grimoire.Types.Ability.List(
                Grimoire.root.trees.local.ldap._Ability.EntriesList.fromLDAPEntries(conn, dn))
            return A(Ps([('filter', A(Grimoire.Types.SubsetType.derive(current),
                                      'Abilities you wish to grant'))]),
                     Grimoire.Types.Formattable(
                         'Grant some of your own (transferable) abilities to %(path)s',
                         path=Grimoire.Types.DN(path)))
                
    class change_ability_cancel_allow_dn(DNM, CAM, SM):
        __path__ = ['change', 'ability', 'cancel', 'allow', 'dn', '$ldapservername']
        _pathType = Grimoire.Types.DN
        def _call(self, path, filter):
            conn = self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                    ['local', 'ldap', 'admin', 'conn'], cache=True))
            path = list(Grimoire.Utils.Reverse(path))
            dn = string.join(['cn=security'] + path, ',')
            abilityLock.acquire()
            try:
                Grimoire.root.trees.local.ldap._Ability.EntriesList.fromLDAPEntries(conn, dn).cancelAllow(filter).toLDAPEntry(conn, dn)
            finally:
                abilityLock.release()
            return A(None,
                     'Successfully canceled access allowance')

    class change_ability_deny_dn(DNM, DM, SM):
        __path__ = ['change', 'ability', 'deny', 'dn', '$ldapservername']
        _pathType = Grimoire.Types.DN
        def _call(self, path, ability):
            conn = self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                    ['local', 'ldap', 'admin', 'conn'], cache=True))
            path = list(Grimoire.Utils.Reverse(path))
            dn = string.join(['cn=security'] + path, ',')
            abilityLock.acquire()
            try:
                Grimoire.root.trees.local.ldap._Ability.EntriesList.fromLDAPEntries(conn, dn).deny(ability).toLDAPEntry(conn, dn)
            finally:
                abilityLock.release()
            return A(None,
                     'Successfully denied access')

    class change_ability_cancel_deny_dn(DNM, CAM, SM):
        __path__ = ['change', 'ability', 'cancel', 'deny', 'dn', '$ldapservername']
        _pathType = Grimoire.Types.DN
        def _call(self, path, filter):
            conn = self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                    ['local', 'ldap', 'admin', 'conn'], cache=True))
            path = list(Grimoire.Utils.Reverse(path))
            dn = string.join(['cn=security'] + path, ',')
            abilityLock.acquire()
            try:
                Grimoire.root.trees.local.ldap._Ability.EntriesList.fromLDAPEntries(conn, dn).cancelDeny(filter).toLDAPEntry(conn, dn)
            finally:
                abilityLock.release()
            return A(None,
                     'Successfully canceled access denial')

    class create_ability_dn(DNM, SEM, SM):
        __path__ = ['create', 'ability', 'dn', '$ldapservername']
        _pathType = Grimoire.Types.DN
        def _call(self, path, ability):
            conn = self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                    ['local', 'ldap', 'admin', 'conn'], cache=True))
            dn = string.join(['cn=security'] + list(Grimoire.Utils.Reverse(path)), ',')
            abilityLock.acquire()
            try:
                Grimoire.root.trees.local.ldap._Ability.EntriesList.fromLDAPEntries(conn, dn).setUnion(ability).toLDAPEntry(conn, dn)
            finally:
                abilityLock.release()
            return A(None,
                     'Successfully set abilities')

    class delete_ability_dn(DNM, USEM, SM):
        __path__ = ['delete', 'ability', 'dn', '$ldapservername']
        _pathType = Grimoire.Types.DN
        def _call(self, path, ability):
            conn = self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                    ['local', 'ldap', 'admin', 'conn'], cache=True))
            dn = string.join(['cn=security'] + list(Grimoire.Utils.Reverse(path)), ',')
            abilityLock.acquire()
            try:
                Grimoire.root.trees.local.ldap._Ability.EntriesList.fromLDAPEntries(conn, dn).setMinus(ability).toLDAPEntry(conn, dn)
            finally:
                abilityLock.release()
            return A(None,
                     'Successfully unset some abilities')

    class caap(UM, AM, SM): __path__ = ['change', 'ability', 'allow', 'people', '$ldapservername']
    class caag(GM, AM, SM): __path__ = ['change', 'ability', 'allow', 'groups', '$ldapservername']
    class cacap(UM, CAM, SM): __path__ = ['change', 'ability', 'cancel', 'allow', 'people', '$ldapservername']
    class cacag(GM, CAM, SM): __path__ = ['change', 'ability', 'cancel', 'allow', 'groups', '$ldapservername']

    class cadp(UM, DM, SM): __path__ = ['change', 'ability', 'deny', 'people', '$ldapservername']
    class cadg(GM, DM, SM): __path__ = ['change', 'ability', 'deny', 'groups', '$ldapservername']
    class cacdp(UM, CDM, SM): __path__ = ['change', 'ability', 'cancel', 'deny', 'people', '$ldapservername']
    class cacdg(GM, CDM, SM): __path__ = ['change', 'ability', 'cancel', 'deny', 'groups', '$ldapservername']

    class crap(UM, SEM, SM): __path__ = ['create', 'ability', 'people', '$ldapservername']
    class crag(GM, SEM, SM): __path__ = ['create', 'ability', 'groups', '$ldapservername']
    class dap(UM, USEM, SM): __path__ = ['delete', 'ability', 'people', '$ldapservername']
    class dag(GM, USEM, SM): __path__ = ['delete', 'ability', 'groups', '$ldapservername']
