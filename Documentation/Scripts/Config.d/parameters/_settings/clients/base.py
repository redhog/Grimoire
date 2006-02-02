## General client configuration ##

# Default tree to connect to
# set(['tree'], '_')
# set(['tree'], '_.trees.local.client')
# set(['tree'], '_.trees.local.login("the LDAP tree on example.com", _.trees.remote.dirt.example\.com().trees.local.ldap)')
# This allows seamless integration between the webware UI client and
# some website that uses LDAP for authentication using HTTP AUTH. You
# must enable passing of the HTTP_AUTHORIZATIOn variable to the
# webware script in the webserver for this to work, however.
# set(['tree'], '_.trees.remote.dirt.example\.com().trees.local.ldap(_.directory.get.parameters(["clients", "html", "auth", "username"]), _.directory.get.parameters(["clients", "html", "auth", "password"]))')

# Commands to perform at startup
# set(['initcommands'], ['_.trees.introspection.mount(['otherserver'], _.trees.remote.dirt.otherserver())'])

# import Grimoire.Types.Ability
# set.parameters(['hide'],
#                Grimoire.Types.Ability.List([(Grimoire.Types.Ability.Ignore, ['directory']),
#                                             (Grimoire.Types.Ability.Ignore, ['trees']),
#                                             (Grimoire.Types.Ability.Ignore, ['introspection']),
#                                             (Grimoire.Types.Ability.Allow, [])]))
