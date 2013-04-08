######## The Cyurs Grimoire tree (_.local.cyrus) ########

# Information for connecting to the Cyrus IMAPd server
set(['server', 'host'], 'localhost')
set(['server', 'port'], None) # Defaults to 143...
set(['username'], 'cyrus')
#set(['password'], 'changethisdefaultpassword')
set(['password'], None)

# Access to the cyrus tree is only allowed by users who specify
# the correct username and password as specified here.
set(['login', 'username'], 'cyrus')
# set(['login', 'password'], 'changethisdefaultpassword')
# Remove the next line when you have set the above password
# set(['login', 'password'], None)
set(['login', 'password'], None)

# Name of Cyrus Grimoire server - must be specified.
# treevar('cyrusservername', ['cyrusserver', 'gazonkware', 'com'])
treevar('cyrusservername', ['cyrusserver'])
