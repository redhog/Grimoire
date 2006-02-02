import Grimoire.Performer, Grimoire.Utils, Grimoire.Types
import string, ldap, types

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class group_addMember(Grimoire.Performer.SubMethod):
        __path__ = ['group', 'add member', '$ldapservername']
        __related_group__ = ['group']
        def _call(self, path, member):
            member = Grimoire.Utils.encode(member, 'ascii')
            def unlocked():
                conn = self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                    ['local', 'ldap', 'admin', 'conn'], cache=True)
                dnpath = ['ou=Groups'] + ['ou=' + item for item in path]
                dn = unicode(Grimoire.Types.DN(conn.realm) + dnpath)
                
                try:
                    memberPath = self._getpath(
                        Grimoire.Types.MethodBase, 1,
                        ['list', 'ldapentries', '$ldapservername', 'ou=People']
                        )(filter = 'uid=%s' % member, stripTypes = 1)[0][1]
                    memberHomegroupPath = memberPath[:-1]
                    memberdn = ['ou=People'] + ['ou=' + item for item in memberHomegroupPath] + ['uid=' + member]
                except IndexError:
                    raise Exception(
                        Grimoire.Types.Formattable(
                            "Unknown user %(name)s",
                            name=member))

                homedirPath = self._getpath(Grimoire.Types.TreeRoot,
                                            path=['directory', 'get', 'ldap'] + memberdn,
                                            )(['cn=defaults', 'grimoireHomedirPath'])[0].split('.')
                clientGroupPath = self._getpath(Grimoire.Types.TreeRoot,
                                                path=['directory', 'get', 'ldap'] + list(Grimoire.Types.DN(dnpath)),
                                                )(['cn=defaults', 'grimoireClientHomedirPath'])[0].split('.')
                try:
                    self._getpath(Grimoire.Types.MethodBase, 1,
                                  ['create', 'directory'] + homedirPath + memberHomegroupPath + ['group.users', member]
                                  )('shared', uid=0, gid=0)
                except:
                    pass
                self._getpath(Grimoire.Types.MethodBase, 1,
                              ['create', 'symlink'] + homedirPath + memberHomegroupPath + ['group.users', member, 'shared']
                              )(unicode(Grimoire.Types.UNIXGroup(['groups'] + path)),
                                clientGroupPath + path + ['group.contents'],
                                0, 0)

                try:
                    conn.modify_s(dn, [(ldap.MOD_ADD, 'memberUid', member)])
                except ldap.TYPE_OR_VALUE_EXISTS:
                    raise ValueError('User is already a group member')
                return A(None, 'Member successfully added to group')
            return self._callWithUnlockedTree(unlocked)

        __dir_allowall__ = False
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 1,
                                      ['list', 'ldapentries', '$ldapservername', 'Groups'] + path
                                      )(depth, filter = 'objectClass=GrimoireGroup', addType='ou'))

        def _params(self, path):
            return A(Ps([('member', A(types.StringType,
                                      "Member to add"))]),
                     Grimoire.Types.Formattable('Add a user as a member to the group %(group)s',
                                                group=Grimoire.Types.UNIXGroup(['groups'] + path)))

    class group_removeMember(Grimoire.Performer.SubMethod):
        __path__ = ['group', 'remove member', '$ldapservername']
        __related_group__ = ['group']
        def _call(self, path, member):
            member = Grimoire.Utils.encode(member, 'ascii')
            def unlocked():
                conn = self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                    ['local', 'ldap', 'admin', 'conn'], cache=True)
                dnpath = ['ou=Groups'] + ['ou=' + item for item in path]
                dn = unicode(Grimoire.Types.DN([conn.realm] + dnpath))

                warning = None
                try:
                    memberPath = self._getpath(
                        Grimoire.Types.MethodBase, 1,
                        ['list', 'ldapentries', '$ldapservername', 'ou=People']
                        )(filter = 'uid=%s' % member, stripTypes = 1)[0][1]
                    memberHomegroupPath = memberPath[:-1]
                    memberdn = ['ou=People'] + ['ou=' + item for item in memberHomegroupPath] + ['uid=' + member]
                    homedirPath = self._getpath(Grimoire.Types.TreeRoot,
                                                path=['directory', 'get', 'ldap'] + memberdn
                                                )(['cn=defaults', 'grimoireHomedirPath'])[0].split('.')
                    self._getpath(Grimoire.Types.MethodBase, 1,
                                  ['delete', 'file'] + homedirPath + memberHomegroupPath + ['group.users', member, 'shared', unicode(Grimoire.Types.UNIXGroup(['groups'] + path))]
                                  )()
                except Exception, e:
                    warning = e

                try:
                    conn.modify_s(dn, [(ldap.MOD_DELETE, 'memberUid', member)])
                except ldap.NO_SUCH_ATTRIBUTE:
                    raise ValueError('User was not a member of the group')
                return A(warning, 'Member successfully removed from group')
            return self._callWithUnlockedTree(unlocked)

        __dir_allowall__ = False
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 1, ['list', 'ldapentries', '$ldapservername', 'Groups'] + path
                                      )(depth, 'ou=*', addType='ou'))

        def _params(self, path):
            return A(Ps([('member', A(types.StringType,
                                      "Member to remove"))]),
                     Grimoire.Types.Formattable('Remove a user from the group %(group)s',
                                                group=Grimoire.Types.UNIXGroup(['groups'] + path)))
