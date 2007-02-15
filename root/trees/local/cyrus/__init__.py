import Grimoire.Performer, Grimoire.Types, types, cyruslib

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class unprotected_cyrus(Grimoire.Performer.Method):
        def _call(self, host = None, port = None, cyrusUsername = None, cyrusPassword = None):
            directory = self._callWithUnlockedTree(lambda: self._getpath(Grimoire.Types.TreeRoot).directory.new())
            setParam = directory.directory.set.parameters
            getParam = directory.directory.get.parameters

            if host: setParam(['local', 'cyrus', 'server', 'host'], host)
            rHost = getParam(['local', 'cyrus', 'server', 'host'], None)

            if port: setParam(['local', 'cyrus', 'server', 'port'], port)
            rPort = getParam(['local', 'cyrus', 'server', 'port'], None)

            if cyrusUsername: setParam(['local', 'cyrus', 'username'], cyrusUsername)
            rCyrusUsername = getParam(['local', 'cyrus', 'username'], 'cyrus')

            if cyrusPassword: setParam(['local', 'cyrus', 'password'], cyrusPassword)
            rCyrusPassword = getParam(['local', 'cyrus', 'password'], None)

            connParams = {}
            if rHost is not None: connParams['host'] = rHost
            if rPort is not None: connParams['port'] = rPort
            conn = cyruslib.CYRUS(**connParams)
            conn.login(rCyrusUsername, rCyrusPassword)
            setParam(['local', 'cyrus', 'conn'], conn)

            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase).load.standardtree(
                    __name__ + '._performers',
                    ['parameters'],
                    ['local', 'cyrus', 'initcommands'],
                    directory = directory))
        def _params(self):
            return A(Ps([('host',
                          A(types.StringType,
                            'Cyrus IMAPd host')),
                         ('port',
                          A(types.IntType,
                            'Cyrus IMAPd port')),
                         ]),
                     'Returns a tree for manipulating the cyrus mailserver')

    class cyrus(Grimoire.Performer.Method):
        def _call(self, userId, password, host = None, port = None):
            if (userId != self._callWithUnlockedTree(
                    lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                        ['local', 'cyrus', 'login', 'username'])) or
                password != self._callWithUnlockedTree(
                    lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                        ['local', 'cyrus', 'login', 'password']))):
                raise Exception('Bad username or password')
            return self._callWithUnlockedTree(lambda:
                self._getpath(Grimoire.Types.MethodBase).unprotected.cyrus(host, port))
        def _params(self):
            return A(Ps([('userId',
                          A(types.StringType,
                            'User name')),
                         ('password',
                          A(Grimoire.Types.PasswordType,
                            'User password')),
                         ('host',
                          A(types.StringType,
                            'Cyrus IMAPd host')),
                         ('port',
                          A(types.IntType,
                            'Cyrus IMAPd port')),
                         ],
                        2),
                     'Returns a tree for manipulating the cyrus mailserver')
