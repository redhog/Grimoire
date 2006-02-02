import Grimoire.Performer, Grimoire.Types, ldap, thread

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

getUniqueIdLock = thread.allocate_lock()

class Performer(Grimoire.Performer.Base):
    class uniqueId(Grimoire.Performer.Method):
        __path__ = ['uniqueId', '$ldapservername']
        def _call(self, category):
            conn = self._callWithUnlockedTree(self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters,
                                              ['local', 'ldap', 'admin', 'conn'])
            dn = 'cn=maxId,' + conn.realm
            category = Grimoire.Utils.encode(category, 'ascii')

            getUniqueIdLock.acquire()
            try:
                id = conn.search(dn, ldap.SCOPE_BASE, attrlist=[category])
                res = conn.result(id)[1][0][1][category][0]
                res = int(res)
                conn.modify_s(dn, [(ldap.MOD_REPLACE, category, Grimoire.Utils.encode(res + 1, 'ascii'))])
                return res
            finally:
                getUniqueIdLock.release()
        
        def _params(self):
            return A(Ps([('category', A(Grimoire.Types.UsernameType,
                                        'Category/type of object to create a unique id for'))]),
                     'Create a unique id number')
