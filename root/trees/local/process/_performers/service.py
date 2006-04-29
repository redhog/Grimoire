import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, types

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive


class Performer(Grimoire.Performer.Base):
    class list_services(Grimoire.Performer.SubMethod):
        __path__ = ['list', 'services', '$processservername']
        __related_group__ = ['initd']
        def _call(self, path, depth = Grimoire.Performer.UnlimitedDepth):
            """This is a quick and dirty hack, ok?"""
            if depth == -1: depth = Grimoire.Performer.UnlimitedDepth
            cpid, cstdin, cstdout, cstderr = Grimoire.Utils.popen("chkconfig",
                                                                  ("chkconfig", "--list"),
                                                                  bindpty = False)
            result = []
            for items in [line.split('\t') for line in cstdout]:
                service = items[0].strip()
                for item in [item.strip() for item in items[1:]]:
                    result.append((0, [item.strip()[2:]]))
                    result.append((0, [item.strip()[2:], item[0]]))
                    result.append((1, [item.strip()[2:], item[0], service]))
            cstdin.close()
            cstdout.close()
            cstderr.close()
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

    class enable_service(Grimoire.Performer.SubMethod):
        __path__ = ['enable', 'service', '$processservername']
        __related_group__ = ['service']
        __dir_allowall__ = False
        def _call(self, path):
            cpid, cstdin, cstdout, cstderr = Grimoire.Utils.popen("chkconfig",
                                                                  ("chkconfig", "--level", path[0], path[1], "on"),
                                                                  bindpty = False)
            err = cstderr.read()
            cstdin.close()
            cstdout.close()
            cstderr.close()
            status = waitpit(cpid)[1]
            if status != 0:
                raise Exception(stderr, status)
            return stdout
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(lambda: self._getpath(Grimoire.Types.MethodBase,
                                                                    path = ['list', 'services', '$processservername', 'off'] + path)(depth))

        def _params(self, path):
            return A(Ps([]),
                     Grimoire.Types.Formattable(
                         'Enable %(service)s in runlevel %(runlevel)s',
                         service = path[1],
                         runlevel = path[0]))

    class disable_service(Grimoire.Performer.SubMethod):
        __path__ = ['disable', 'service', '$processservername']
        __related_group__ = ['service']
        __dir_allowall__ = False
        def _call(self, path):
            cpid, cstdin, cstdout, cstderr = Grimoire.Utils.popen("chkconfig",
                                                                  ("chkconfig", "--level", path[0], path[1], "off"),
                                                                  bindpty = False)
            err = cstderr.read()
            cstdin.close()
            cstdout.close()
            cstderr.close()
            status = waitpit(cpid)[1]
            if status != 0:
                raise Exception(stderr, status)
            return stdout
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(lambda: self._getpath(Grimoire.Types.MethodBase,
                                                                    path = ['list', 'services', '$processservername', 'on'] + path)(depth))

        def _params(self, path):
            return A(Ps([]),
                     Grimoire.Types.Formattable(
                         'Disable %(service)s in runlevel %(runlevel)s',
                         service = path[1],
                         runlevel = path[0]))
