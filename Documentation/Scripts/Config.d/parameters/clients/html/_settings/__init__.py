## Grimweb (Webware client) ##

# URL to where the Grimweb webware page is installed 
#set(['url'], 'http://example.com/WebWare/GrimWeb')
set(['url'], '/WebWare/GrimWeb')

# URL to where the Grimweb static pages and images are installed. This
# one defaults to the same as the one above, in which case the static
# content is served through Webware too (which works, but is kind of
# slow). Note that both of them should point to the same physical
# directory on disk
# (Grimoire/root/clients/html/funformkit/webware/_grimwebcontext/),
# but one as a Webware context, the other as a webserver
# alias/symlink.
# set(['static', 'url'], 'http://example.com/GrimWeb-static')
set(['static', 'url'], '/GrimWeb-static')

# Look&feel
# set(['theme', 'pictures', 'dir'], 'http://example.com/GrimWeb-static/pictures')
set(['theme', 'pictures', 'pattern'], 'grime.%(name)s.gif')
# set(['theme', 'body', 'colour', 'background'], '#ffffff')
# set(['theme', 'body', 'colour', 'text'], '#000000')
# set(['theme', 'body', 'colour', 'link'], '#000000')
# set(['theme', 'body', 'colour', 'vlink'], '#000000')
# set(['theme', 'menu', 'colour', 'background'], '#dfdfdf')
# set(['theme', 'menu', 'colour', 'text'], '#000000')
# set(['theme', 'menu', 'colour', 'link'], '#000000')
# set(['theme', 'menu', 'colour', 'vlink'], '#000000')
# set(['theme', 'menu', 'font', 'face'], 'sans-serif,Arial,geneva,helvetica')
# set(['theme', 'menu', 'font', 'size'], '+0')
# set(['theme', 'form', 'colour', 'background'], '#ffffff')
# set(['theme', 'form', 'colour', 'text'], '#000000')
# set(['theme', 'form', 'colour', 'link'], '#000000')
# set(['theme', 'form', 'colour', 'vlink'], '#000000')
# set(['theme', 'form', 'box', 'colour'], '#aea081')

# Tree configuration
# Any config that can go into
# Config.d/parameters/clients/_settings/__init__.py can go here. In
# addition, you can use the command below to get seamless integration
# between the webware UI client and some website that uses LDAP for
# authentication using HTTP AUTH. You must enable passing of the
# HTTP_AUTHORIZATION variable to the webware script in the webserver
# for this to work, however.
# set(['tree'], '_.trees.remote.dirt.example\.com().trees.local.ldap(_.directory.get.parameters(["clients", "html", "auth", "username"]), _.directory.get.parameters(["clients", "html", "auth", "password"]))')
