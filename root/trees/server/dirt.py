import Grimoire.Performer, Grimoire.Types, Grimoire.Types.Ability
import Grimoire.Utils, Grimoire.Utils.Serialize.RPC
import types, socket, threading, string, exceptions, os, sys

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

if (os.sysconf_names.has_key("SC_OPEN_MAX")):
    maxfd = os.sysconf("SC_OPEN_MAX")
else:
    maxfd = 256 # default maximum

def unixDaemon(target, targetFiles = [], ourHomeDir='/'):
    """From http://starship.python.net/crew/jjkunce/python/daemonize.py"""
    pid = os.fork()
    if pid != 0:
        for z in targetFiles:
            try: os.close(z)
            except: pass
        return pid
    os.setsid()
    os.chdir(ourHomeDir)
    os.umask(0)
    for fd in range(0, maxfd):
        if fd not in targetFiles:
            try: os.close(fd)
            except: pass
    sys.stdin = open('/dev/null', 'r')
    sys.stdout = open('/dev/null', 'w')
    sys.stderr = open('/dev/null', 'w')
    target()

class Performer(Grimoire.Performer.Base):
    class socket_bound_dirt(Grimoire.Performer.Method):
        def _call(self, description, sock, obj = None, daemonic = True, fork = False, *arg, **kw):
            tree = obj
            if tree is None:
                tree = '_'
            if not isinstance(tree, Grimoire.Performer.Performer):
                tree = Grimoire.Performer.Restrictor(
                    Grimoire.Performer.Composer(
                        Grimoire.Performer.Prefixer(
                            ['introspection'],
                            self._callWithUnlockedTree(lambda: self._getpath(Grimoire.Types.MethodBase, 1).introspection())),
                        Grimoire.Performer.Isolator(self._getpath(Grimoire.Types.TreeRoot).introspection.eval(tree))),
                    Grimoire.serverTreesAbility)
            server = Grimoire.Utils.Serialize.RPC.BindingServer(
                sock,
                Grimoire.Utils.Curry(
                    self._getpath(Grimoire.Types.MethodBase, 1).rpc.binding.dirt(),
                    tree = Grimoire.Performer.Composer(
                        Grimoire.Performer.Prefixer(['treestore'], self._getpath(Grimoire.Types.MethodBase).treestore()),
                        Grimoire.Performer.Prefixer(['treestore', 'call', 'public'], Grimoire.Performer.Isolator(tree)))))
            if fork:
                res = unixDaemon(target = server.serve_forever, targetFiles = [sock.fileno()])
            else:
                res = threading.Thread(
                    target = server.serve_forever,
                    name = description)
                res.setDaemon(daemonic)
                res.start()
            return A(res, description)
        def _params(self, path):
            return A(Ps([('description', A(types.StringType, 'Description of the connection')),
                         ('sock', A(socket.socket,
                                   'Underlaying transport socket')),
                         ('obj', A(Grimoire.Performer.Performer,
                                   'Performer to serve')),
                         ('daemonic', A(Grimoire.Types.BooleanType,
                                        'Whether to detach the server thread or not (if detached, '
                                        'the Python process will not terminate until all server threads has terminated)')),
                         ('fork', A(Grimoire.Types.BooleanType,
                                    'Whether to run the server in a new process or not'))],
                        2),
                     'Serves an object to the outside world using DIRT over some provided (bound) socket-object')

    class findport(Grimoire.Performer.SubMethod):
        def _call(self, path, defaultport):
            host = ''
            port = defaultport
            if path and 1 not in map(lambda c: c in string.digits, path[0]):
                host = path[0]
                path = path[1:]
            if path:
                port = int(path[0])
            return (host, port)
        def _dir(self, path, depth):
            return []
        def _params(self, path):
            return A(Ps([('defaultport', A(types.IntType,
                                           'Default port to use'))]),
                     'Convert a path to a (host, port) specification')

    class socket_dirt(Grimoire.Performer.SubMethod):
        def _call(self, path, protocolName, sock, obj = None, *arg, **kw):
            host, port = self._getpath(Grimoire.Types.MethodBase, path=['findport'] + path
                                       )(Grimoire.Types.protocolMapping[protocolName][1])
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((host, port))
            sock.setblocking(1)
            return self._getpath(levels=1).bound.dirt(
                Grimoire.Types.Formattable(
                    '%(proto)s server for %(obj)s on %(host)s:%(port)s',
                    proto=protocolName,
                    obj=obj,
                    host=host,
                    port=port),
                sock, obj, *arg, **kw)
        def _dir(self, path, depth):
            return []
        def _params(self, path):
            ps = Grimoire.Types.getValue(
                self._getpath(Grimoire.Types.TreeRoot,
                              path=['introspection', 'params'] + self._physicalGetpath(levels=-1, path = ['bound', 'dirt'])._pathForSelf()
                              )())
            return A(Ps([('protocolName', A(types.StringType, 'Name of protocol (used to look up default port)'))] + ps.arglist,
                        1 + ps.required, ps.resargstype, ps.reskwtype, ps.convertType),
                     'Serves an object to the outside world using DIRT over some provided unbound socket-object')

    class ssl_dirt(Grimoire.Performer.SubMethod):
        def _call(self, path, *arg, **kw):
            return self._getpath(
                Grimoire.Types.MethodBase, path=['socket', 'dirt'] + path
                )('ssl.dirt',
                  self._callWithUnlockedTree(lambda: self._getpath(Grimoire.Types.MethodBase, 1).rpc.listen.ssl(*arg, **kw)),
                  *arg, **kw)
        def _dir(self, path, depth):
            return [(1, [])]
        def _params(self, path):
            ps = Grimoire.Types.getValue(
                self._getpath(Grimoire.Types.TreeRoot,
                              path=['introspection', 'params'] + self._physicalGetpath(Grimoire.Types.MethodBase, 0, ['socket', 'dirt'])._pathForSelf()
                              )())
            return A(Ps(ps.arglist[3:], ps.required - 3, ps.resargstype, ps.reskwtype, ps.convertType),
                     'Serves an object to the outside world using DIRT over ssl')

    class dirt(Grimoire.Performer.SubMethod):
        def _call(self, path, *arg, **kw):
            return self._getpath(
                Grimoire.Types.MethodBase, path=['socket', 'dirt'] + path
                )('dirt',
                  self._callWithUnlockedTree(lambda: self._getpath(Grimoire.Types.MethodBase, 1).rpc.listen.tcp(*arg, **kw)),
                  *arg, **kw)
        def _dir(self, path, depth):
            return [(1, [])]
        def _params(self, path):
            ps = Grimoire.Types.getValue(
                self._getpath(Grimoire.Types.TreeRoot,
                              path=['introspection', 'params'] + self._physicalGetpath(Grimoire.Types.MethodBase, -1, ['socket', 'dirt'])._pathForSelf()
                              )())
            return A(Ps(ps.arglist[2:], ps.required - 2, ps.resargstype, ps.reskwtype, ps.convertType),
                     'Serves an object to the outside world using DIRT over ssl')
