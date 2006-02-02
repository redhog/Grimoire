import Grimoire.Utils, ldap.ldapobject, types

# This is a fix for newer versions of python-ldap, which doesn't allow
# unicode-strings / objects with __unicode__ as modlist values. It
# encodes all values in utf-8, as they should be, prior to sending
# them off to the original method (modify or add).

old_modify = ldap.ldapobject.LDAPObject.modify
def modify(self, dn, modlist):
    new_modlist = []
    for (mod_op, mod_type, mod_vals) in modlist:
        if isinstance(mod_vals, types.BaseStringType):
            mod_vals = (mod_vals,)
        new_modlist.append(
            (mod_op, mod_type,
             [Grimoire.Utils.encode(value, 'utf-8')
              for value in mod_vals]))
    return old_modify(self, dn, new_modlist)
modify.__doc__ = old_modify.__doc__
modify.__module__ = 'ldap.ldapobject'
ldap.ldapobject.LDAPObject.modify = types.MethodType(modify, None, ldap.ldapobject.LDAPObject)

old_add = ldap.ldapobject.LDAPObject.add
def add(self, dn, modlist):
    new_modlist = []
    for (mod_type, mod_vals) in modlist:
        if isinstance(mod_vals, types.BaseStringType):
            mod_vals = (mod_vals,)
        new_modlist.append(
            (mod_type,
             [Grimoire.Utils.encode(value, 'utf-8')
              for value in mod_vals]))
    return old_add(self, dn, new_modlist)
add.__doc__ = old_add.__doc__
add.__module__ = 'ldap.ldapobject'
ldap.ldapobject.LDAPObject.add = types.MethodType(add, None, ldap.ldapobject.LDAPObject)
