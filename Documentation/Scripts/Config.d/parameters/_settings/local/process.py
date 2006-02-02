## The process tree ##

# Access to the process tree is only allowed by users who specify
# the correct username and password as specified here.
set(['login', 'username'], 'process')
# set(['login', 'password'], 'changethisdefaultpassword')
# Remove the next line when you have set the above password
set(['login', 'password'], None)

# Commands to perform at startup.
# set(['initcommands'], [])

# Name of file-server - must be specified.
treevar('processservername', ['processserver'])
# How to set a complete domain name
# treevar('processservername', ['processserver', 'gazonkware', 'com'])
