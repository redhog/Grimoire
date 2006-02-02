## The filesystem tree ##

# Access to the filesystem tree is only allowed by users who specify
# the correct username and password as specified here.
set(['login', 'username'], 'filesystem')
# set(['login', 'password'], 'changethisdefaultpassword')
# Remove the next line when you have set the above password
set(['login', 'password'], None)

# Commands to perform at startup.
# set(['initcommands'], [])

# Name of file-server - must be specified.
treevar('fileservername', ['fileserver'])
# How to set a complete domain name
# treevar('fileservername', ['fileserver', 'gazonkware', 'com'])

# "chroot" to this directory before serving the tree (not a real
# chroot, just prepend this path to all paths :)
# The path is expressed a s a list of directory names.
# set(['basepath'], [])
