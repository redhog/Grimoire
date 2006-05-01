import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, types, os, time

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive


class ChangeService(Grimoire.Performer.SubMethod):
    __related_group__ = ['service']
    __dir_allowall__ = False
    def _call(self, path):
        filepath = os.path.join("/etc/init.d", path[0])
        out, err = Grimoire.Utils.system(filepath,(filepath, self.__cmd__, path[0]), onlyOkStatus = True)
        return out
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
        __related_group__ = ['service']
        def _call(self, path, depth = Grimoire.Performer.UnlimitedDepth):
            if depth == -1: depth = Grimoire.Performer.UnlimitedDepth
            if len(path) + depth < 2:
                result = [(0, ['on']),
                          (0, ['off'])]
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
        _dir = _call
        def _params(self, path):
            if path:
                comment = Grimoire.Types.Formattable(
                    'List services that are %(status)s',
                    status=path[0])
            else:
                comment = 'List services'
            return A(Ps([('depth',
                          A(types.IntType,
                            "Only return entries this far down in the tree (-1 means infinity)"))]),
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
