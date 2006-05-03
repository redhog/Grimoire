import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, types

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class ChangeService(Grimoire.Performer.SubMethod):
    __dir_allowall__ = False
    def _call(self, path):
        out, err = Grimoire.Utils.system("chkconfig", ("chkconfig", "--level", path[0], path[1], self.__cmd__), onlyOkStatus = True)
        return out
    def _dir(self, path, depth):
        return self._callWithUnlockedTree(lambda: self._getpath(Grimoire.Types.MethodBase,
                                                                path = ['list', 'services', 'initd', '$processservername', self.__status__] + path)(depth))
    def _related(self, path, depth, objectPath, objectDepth):
        pathForSelf = self._pathForSelf()
        objPrefix = []
        while pathForSelf and pathForSelf[-1].startswith('$'):
            objPrefix[0:0] = [pathForSelf[-1]]
            del pathForSelf[-1]
        description = pathForSelf
        objPrefix, objPrefixLen, which = Grimoire.Performer.getPrefix(self, True,
                                                                      ['service'] + objPrefix,
                                                                      len(['service'] + objPrefix),
                                                                      [], True)
        if len(objectPath) + objectDepth <= objPrefixLen:
            result = [(0, objPrefix, pathForSelf, [])]
        else:
            result = Grimoire.Utils.Map(lambda (leaf, path): (leaf, objPrefix + path[1:], pathForSelf + path[:1], path),
                                        self._treeOp([], 'dir', depth=Grimoire.Performer.UnlimitedDepth))
        return Grimoire.Performer.DirListFilter(
            path, depth,
            Grimoire.Performer.DirListFilter(objectPath, objectDepth,
                                             result),
            False, 3)
    def _params(self, path):
        return A(Ps([]),
                 Grimoire.Types.Formattable(
                     '%(name)s %(service)s in runlevel %(runlevel)s',
                     name = self.__name__,
                     service = path[1],
                     runlevel = path[0]))

class Performer(Grimoire.Performer.Base):
    class list_services(Grimoire.Performer.SubMethod):
        __path__ = ['list', 'services', 'initd', '$processservername']
        def _call(self, path, depth = Grimoire.Performer.UnlimitedDepth):
            """This is a quick and dirty hack, ok?"""
            if depth == -1: depth = Grimoire.Performer.UnlimitedDepth
            if len(path) + depth < 3:
                result = [(0, ['on', '0']),
                          (0, ['on', '1']),
                          (0, ['on', '2']),
                          (0, ['on', '3']),
                          (0, ['on', '4']),
                          (0, ['on', '5']),
                          (0, ['on', '6']),
                          (0, ['off', '0']),
                          (0, ['off', '1']),
                          (0, ['off', '2']),
                          (0, ['off', '3']),
                          (0, ['off', '4']),
                          (0, ['off', '5']),
                          (0, ['off', '6'])]
            else:
                lines, err = Grimoire.Utils.system("chkconfig", ("chkconfig", "--list"), onlyOkStatus = True)
                result = []
                for items in [line.split('\t') for line in lines.split('\n')]:
                    service = items[0].strip()
                    for item in [item.strip() for item in items[1:]]:
                        result.append((1, [item.strip()[2:], item[0], service]))
            return Grimoire.Performer.DirListFilter(path, depth, result)
        def _dir(self, path, depth):
            return [(1, [])]
        def _params(self, path):
            return A(Ps([('depth',
                          A(types.IntType,
                            "Only return entries this far down in the tree (-1 means infinity)"))]),
                     Grimoire.Types.Formattable(
                         'List services under %(path)s',
                         path=Grimoire.Types.GrimoirePath(path)))

    class enable_service(ChangeService):
        __path__ = ['enable', 'service', '$processservername']
        __name__ = 'Enable'
        __cmd__ = 'on'
        __status__ = 'off'

    class disable_service(ChangeService):
        __path__ = ['disable', 'service', '$processservername']
        __name__ = 'Disable'
        __cmd__ = 'off'
        __status__ = 'on'
