import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, types, os

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive


class ChangeService(Grimoire.Performer.SubMethod):
    __related_group__ = ['service']
    __dir_allowall__ = False
    def _call(self, path):
        filepath = os.path.join("/etc/init.d", path[0])
        out, err = Grimoire.Utils.system(filepath,(filepath, self.__cmd__, path[0]), onlyOkStatus = True)
        return out
    def _related_objdir(self, path, depth):
        return self._callWithUnlockedTree(lambda: self._getpath(Grimoire.Types.MethodBase,
                                                                path = ['list', 'services', 'running', '$processservername', self.__status__] + path)(depth, True))
    def _dir(self, path, depth):
        return self._callWithUnlockedTree(lambda: self._getpath(Grimoire.Types.MethodBase,
                                                                path = ['list', 'services', 'running', '$processservername', self.__status__] + path)(depth))

    def _params(self, path):
        return A(Ps([]),
                 Grimoire.Types.Formattable(
                     '%(name)s %(service)s',
                     name = self.__name__,
                     service = path[0]))

class Performer(Grimoire.Performer.Base):
    class list_services(Grimoire.Performer.SubMethod):
        __path__ = ['list', 'services', 'running', '$processservername']
        def _call(self, path, depth = Grimoire.Performer.UnlimitedDepth, objlisting = False):
            if depth == -1: depth = Grimoire.Performer.UnlimitedDepth
            if len(path) > 2:
                return []
            elif len(path) + depth < 2:
                result = [(0, ['on']),
                          (0, ['off'])]
            elif objlisting:
                # We know that each service will either be on or
                # off, so the object listing should allways
                # contain all of them...
                if len(path) == 2:
                    result = [(1, path)]
                else:
                    dirlist = os.listdir("/etc/init.d")
                    result = [(1, ['on', name]) for name in dirlist] + [(1, ['off', name]) for name in dirlist]
            else:
                if len(path) == 2:
                    filepath = os.path.join("/etc/init.d", path[1])
                    try:
                        status, out, err = Grimoire.Utils.system(filepath, (filepath, "status"))
                        if ['off', 'on'][status == 0] != path[0]:
                            return []
                        result = [(1, path)]
                    except Exception, e:
                        pass
                else:
                    result = []
                    for name in os.listdir("/etc/init.d"):
                        filepath = os.path.join("/etc/init.d", name)
                        try:
                            status, out, err = Grimoire.Utils.system(filepath, (filepath, "status"))
                            status = ['off', 'on'][status == 0]
                            result.append((1, [status, name]))
                        except Exception, e:
                            pass
            return Grimoire.Performer.DirListFilter(path, depth, result)
        def _dir(self, path, depth):
             self._callWithUnlockedTree(lambda: self._getpath(Grimoire.Types.CurrentNode,
                                                                     path = path)(depth))
        def _params(self, path):
            if path:
                comment = Grimoire.Types.Formattable(
                    'List services that are %(status)s',
                    status=path[0])
            else:
                comment = 'List services'
            return A(Ps([('depth',
                          A(types.IntType,
                            "Only return entries this far down in the tree (-1 means infinity)")),
                         ('objlisting',
                          A(types.BooleanType,
                            "Don't bother to check if services are actually running, only return a list of existing services. Used by introspection.object."))]),
                     comment)

    class enable_service(ChangeService):
        __path__ = ['enable', 'service', 'running', '$processservername']
        __cmd__ = "start"
        __status__ = "off"
        __name__ = "Enable"

    class disable_service(ChangeService):
        __path__ = ['disable', 'service', 'running', '$processservername']
        __cmd__ = "stop"
        __status__ = "on"
        __name__ = "Disable"
