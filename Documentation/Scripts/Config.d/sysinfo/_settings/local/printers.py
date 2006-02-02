## The printer tree - commands to communicate with printers ##

# (dead simple implementation: must comply to the form "<command>
# <printername>" except for list, which is just "<command>"). If they
# don't, well, you'd better write yourself some wrappers. ;>
# set(['enable'], '/usr/bin/enable') 
# set(['disable'], '/usr/bin/disable')
# set(['reset'], 'cancel -a')
# set(['listprinters'], 'lpstat -a')
# set(['listqueue'], 'lpstat -o')
