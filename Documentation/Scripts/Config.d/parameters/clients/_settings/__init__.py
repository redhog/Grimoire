## General client configuration ##

# Default tree to connect to
# set(['tree'], '_')
# set(['tree'], '_.trees.local.client')
# set(['tree'], '_.trees.local.login("the LDAP tree on example.com", _.trees.remote.dirt.example\.com().trees.local.ldap)')

# Commands to perform at startup
# set(['initcommands'], ['_.trees.introspection.mount(['otherserver'], _.trees.remote.dirt.otherserver())'])


# Filter for what to show at the topp-level of the tree view
# import Grimoire.Types.Ability
# set(['view', 'hide'],
#     Grimoire.Types.Ability.List([(Grimoire.Types.Ability.Ignore, ['directory']),
#                                  (Grimoire.Types.Ability.Ignore, ['trees']),
#                                  (Grimoire.Types.Ability.Ignore, ['introspection']),
#                                  (Grimoire.Types.Ability.Ignore, ['clients']),
#                                  (Grimoire.Types.Ability.Ignore, ['test']),
#                                  (Grimoire.Types.Ability.Allow, [])]))

# Filter for what to show in new trees added to the tree view. This
# _includes_ the topp-level tree.
# import Grimoire.Types.Ability
# set(['hide'],
#     Grimoire.Types.Ability.List([(Grimoire.Types.Ability.Ignore, ['directory']),
#                                  (Grimoire.Types.Ability.Ignore, ['trees']),
#                                  (Grimoire.Types.Ability.Ignore, ['introspection']),
#                                  (Grimoire.Types.Ability.Allow, [])]))
