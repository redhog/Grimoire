## The LDAP Grimoire tree (_.local.ldap) ##

# Domain name of LDAP server
set(['server'], 'ldap')

# Base DN. All access of the LDAP database is done under this DN.
set(['realm'], 'dc=example,dc=com')

# Note: All changes to LDAP are done using the admin account specified
# below. Access control for users is done using the Grimoire access
# control method (see Overview.txt), not the limited LDAP 1access
# controls.
# Admin DN, relative to the base DN above.
#set(['admin', 'dn'], 'cn=admin')
# Admin password.
set(['admin', 'password'], 'changethisdefaultpassword')

# The user which should own mail directories. If unset, each user will
# own his/her own mail directory.
# set(['create', 'maildir', 'ownerAccount'], 'postfix')

# The dn for the client machines group (excluding the realm)
set(['create', 'machine', 'clientGroupDn'], ['ou=Machines'])

# Name of LDAP Grimoire server - must be specified.
# Setting the ldapservername to the empty list makes things look nice
# if users are logging in directly to the LDAP-tree with the GUI, as
# is customary.
treevar('ldapservername', [])
# treevar('ldapservername', ['ldapserver'])
# How to set a complete domain name
# treevar('ldapservername', ['ldapserver', 'gazonkware', 'com'])
