## Command-line client (CLI) ##

# Default tree to connect to
# set(['tree'], '_')
# set(['tree'], '_.trees.local.client')
# set(['tree'], '_.trees.local.login("the LDAP tree on example.com", _.trees.remote.dirt.example\.com().trees.local.ldap)')

# Commands to perform at startup
# set(['initcommands'], ['_.trees.introspection.mount(['otherserver'], _.trees.remote.dirt.otherserver())'])

# import Grimoire.Types.Ability
# set(['hide'],
#     Grimoire.Types.Ability.List([(Grimoire.Types.Ability.Ignore, ['directory']),
#                                  (Grimoire.Types.Ability.Ignore, ['trees']),
#                                  (Grimoire.Types.Ability.Ignore, ['introspection']),
#                                  (Grimoire.Types.Ability.Allow, [])]))

# Default command(s) to perform if no command is given on the command-line
set(['defaultcommands'], ['_.trees.server.dirt("_", 0)'])
