## The printer tree ##

# Access to the printer tree is only allowed by users who specify
# the correct username and password as specified here.
set(['login', 'username'], 'printers')
# set(['login', 'password'], 'changethisdefaultpassword')
# Remove the next line when you have set the above password
set(['login', 'password'], None)

# Commands to perform at startup.
# set(['initcommands'], [])

# Name of printer Grimoire server - must be specified.
treevar('printerservername', ['cups'])
# How to set a complete domain name
# treevar('printerservername', ['cups', 'gazonkware', 'com'])
