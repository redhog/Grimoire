## Propose user tree ##

# Grimoire tree to connect to if using the propose user "webclient"
# locally. This tree must be a local.ldap tree. 
set(['propose', 'user', 'tree'], "_.trees.remote.dirt.localhost().trees.local.ldap('proposeuserclient', 'changethisdefaultpassword')")

# Commands to perform at startup.
# set(['initcommands'], ["_.trees.introspection.mount([], _.trees.remote.dirt.ldapserver().trees.local.ldap('draftchangeaccount', 'changethisdefaultpassword'))"])
