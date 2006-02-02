## The SQueeLer tree ##
# Values for connecting to a SQL user database, and work on
# different tables in that database.

set(['server'], 'sql')
set(['database'], 'squeelerdb')
set(['admin', 'name'], 'postgres')
set(['admin', 'password'], 'changethisdefaultpassword')

# Configurable names of different tables and fields in them
# set(['tables', 'groupabilitytable'], "groupabilities")
# set(['tables', 'groupabilitytable', 'groupidfield'], "usergroup")
# set(['tables', 'grouptable'], "usergroups")
# set(['tables', 'grouptable', 'groupnamefield'], "name")
# set(['tables', 'userabilitytable'], "userabilities")
# set(['tables', 'userabilitytable', 'useridfield'], "user")
# set(['tables', 'usertable'], "users")
# set(['tables', 'usertable', 'usernamefield'], "username")

# Name of SQL server - must be specified.
# Setting the sqlservername to the empty list makes things look nice
# if users are logging in directly to the SQL-tree with the GUI, as
# is customary.
treevar('sqlservername', [])
# treevar('sqlservername', ['sqlserver'])
# How to set a complete domain name
# treevar('sqlservername', ['sqlserver', 'gazonkware', 'com'])

# These can be used to mangle the tree layout a bit - if you want
# individual tables to show up directly under change, create and list,
# set these to the empty lists.
treevar('sqlentry', ['sqlentry'])
treevar('sqlentries', ['sqlentries'])
