## Command-line client (CLI) ##

# Commands to perform at startup. Note that any commands specified
# under ['clients', 'base', 'initcommands'] are executed _prior_ to
# these.
# set(['initcommands'], ['_.trees.introspection.mount(['otherserver'], _.trees.remote.dirt.otherserver())'])

# Default command(s) to perform if no command is given on the command-line
set(['defaultcommands'], ['_.trees.server.dirt("_", 0)'])
