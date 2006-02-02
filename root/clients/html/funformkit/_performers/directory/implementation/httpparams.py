import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, base64

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class get_field(Grimoire.Performer.SubMethod):
        __path__ = ['get', 'parameters', ' ', 'clients', 'html', 'field']
        def _fields(self):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                   ['clients', 'html', 'webware', 'session']).request().fields())
        def _call(self, path):
            return self._fields()[path[0]]
        __dir_allowall__ = False
        def _dir(self, path, depth):
            fields = self._fields()
            if path:
                if path[0] in fields:
                    return [(1, [])]
                return []
            else:
                return [(0, [])] + [(1, [key]) for key in fields.keys()]
        def _params(self, path):
            return A(Ps(),
                     Grimoire.Types.Formattable(
                         'Read the %(attribute)s http field',
                         attribute = path[0]))

    class get_environ(Grimoire.Performer.SubMethod):
        __path__ = ['get', 'parameters', ' ', 'clients', 'html', 'environ']
        def _environ(self):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                   ['clients', 'html', 'webware', 'session']).request()._environ)
        def _call(self, path):
            return self._environ()[path[0]]
        __dir_allowall__ = False
        def _dir(self, path, depth):
            environ = self._environ()
            if path:
                if path[0] in environ:
                    return [(1, [])]
                return []
            else:
                return [(0, [])] + [(1, [key]) for key in environ.keys()]
        def _params(self, path):
            return A(Ps(),
                     Grimoire.Types.Formattable(
                         'Read the %(attribute)s http environment variable',
                         attribute = path[0]))

    class get_cookie(Grimoire.Performer.SubMethod):
        __path__ = ['get', 'parameters', ' ', 'clients', 'html', 'cookie']
        def _cookies(self):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                   ['clients', 'html', 'webware', 'session']).request().cookies())
        def _call(self, path):
            return self._cookies()[path[0]]
        __dir_allowall__ = False
        def _dir(self, path, depth):
            cookies = self._cookies()
            if path:
                if path[0] in cookies:
                    return [(1, [])]
                return []
            else:
                return [(0, [])] + [(1, [key]) for key in cookies.keys()]
        def _params(self, path):
            return A(Ps(),
                     Grimoire.Types.Formattable(
                         'Read the %(attribute)s http cookie',
                         attribute = path[0]))


    class get_auth_username(Grimoire.Performer.Method):
        __path__ = ['get', 'parameters', ' ', 'clients', 'html', 'auth', 'username']
        def _environ(self):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                   ['clients', 'html', 'webware', 'session']).request()._environ)
        def _call(self):
            environ = self._environ()
            auth = environ.get('HTTP_AUTHORIZATION', environ.get('HTTP_CGI_AUTHORIZATION'))
            if not auth.lower().startswith('basic'):
                raise AttributeError
            auth = auth[5:].strip()
            auth = base64.decodestring(auth)
            username, password = auth.split(':', 1)
            return username
        def _params(self):
            return A(Ps(),
                     'Read the http username')

    class get_auth_password(Grimoire.Performer.Method):
        __path__ = ['get', 'parameters', ' ', 'clients', 'html', 'auth', 'password']
        def _environ(self):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                   ['clients', 'html', 'webware', 'session']).request()._environ)
        def _call(self):
            environ = self._environ()
            auth = environ.get('HTTP_AUTHORIZATION', environ.get('HTTP_CGI_AUTHORIZATION'))
            if not auth.lower().startswith('basic'):
                raise AttributeError
            auth = auth[5:].strip()
            auth = base64.decodestring(auth)
            username, password = auth.split(':', 1)
            return password
        def _params(self):
            return A(Ps(),
                     'Read the http password')
