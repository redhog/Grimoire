import Grimoire.Types, Grimoire.Performer, Grimoire.Utils, string, ldap, base64

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class user(Grimoire.Performer.SubMethod):
        __path__ = ['horde', '$ldapservername']
        __related_group__ = ['user']
        def _call(self, path):
            conn = self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot
                                      ).directory.get.parameters(['local', 'ldap', 'admin', 'conn'],
                                                                 cache=True))
            oupath = [ "ou="+elem for elem in path[:-1]]
            # Add 'ou' or 'uid' to all parts of the path
            baseDn = string.join(Grimoire.Utils.Reverse(['ou=People'] + oupath + ["uid="+path[-1]]) + [conn.realm], ',')
            args = {'base': baseDn,
                    'scope': ldap.SCOPE_BASE,
                    'filterstr': 'uid=*',
                    'attrlist': ['objectClass', 'hordePrefs', 'mail', 'cn']}
            res = conn.result(conn.search(**args))

            mod = []

            modObjectClasses = False
            objectClasses = list(res[1][0][1]['objectClass'])
            if 'hordePerson' not in objectClasses:
                objectClasses.append('hordePerson')
                modObjectClasses = True
            if 'top' not in objectClasses:
                objectClasses.append('top')
                modObjectClasses = True
            if modObjectClasses:
                mod.append((ldap.MOD_REPLACE, 'objectClass', objectClasses))
                
            if 'hordePrefs' not in res[1][0][1]:
                # Note on hordePrefs:
                # Each hordePrefs attribute consists of a pair of a
                # keyword and a value separated by a colon. The value
                # is base64-encoded. For some preferences, the value
                # is further encoded in a simple hollerith-based
                # format. Each entry consists of a type, an optional
                # length and a value separated by colons.
                # type    description    format for value
                # i       integer        Length is missing. Value is
                #                        the decimal representation
                #                        of the value.
                # s       string         String is utf-8-encoded and
                #                        surrounded by ". Length is
                #                        number of bytes excluding the
                #                        ".
                # a       array          length is some magic number,
                #                        value is a set of entries
                #                        separated by cemi-colon, and
                #                        surrounded by curly braces. 
                
                prefs = ['identities:' + base64.encodestring(
                    """a:1:{i:0;a:4:{s:2:"id";s:%(fullname_len)s:"%(fullname)s";s:8:"fullname";s:%(fullname_len)s:"%(fullname)s";s:9:"from_addr";s:%(email_len)s:"%(email)s";s:16:"default_identity";s:1:"0";}}"""
                    % {'fullname': Grimoire.Utils.encode(res[1][0][1]['cn'][0], 'utf-8'),
                       'fullname_len': str(len(Grimoire.Utils.encode(res[1][0][1]['cn'][0], 'utf-8'))),
                       'email': Grimoire.Utils.encode(res[1][0][1]['mail'][0], 'utf-8'),
                       'email_len': str(len(Grimoire.Utils.encode(res[1][0][1]['mail'][0], 'utf-8')))
                       }),
                         'default_identity:' + base64.encodestring('0')]
                mod.append((ldap.MOD_REPLACE, 'hordePrefs', prefs))
                
            if mod:
                conn.modify_s(baseDn, mod)
            else:
                return A(None, "Horde web interface already enabled for account")
            return A(None, "Horde web interface enabled for account")
        __dir_allowall__ = False                     
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 2,
                                      ['list', 'ldapentries', '$ldapservername', 'People'] + path
                                      )(depth, filter = 'uid=*', addType = 'ou', endType = 'uid'))
        def _params(self, path):
            return A(Ps([]), Grimoire.Types.Formattable("Enable Horde web interface for the user %(username)s",
                                                        username=path[-1]))
