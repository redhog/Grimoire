import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, types, pwd, grp, socket, os, pty

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class process(Grimoire.Performer.Method):
        __path__ = ['process', '$processservername']
        def _call(self, binary, args = [], env = None, pathLookUp = True, bindstdinout = True, bindpty = True, preExec = None):
            return Grimoire.Utils.popen(binary, args, env, pathLookUp, bindstdinout, bindpty, preExec)

        def _params(self):
            return A(Ps([('binary', A(types.UnicodeType, 'Program to run')),
                         ('args', A(Grimoire.Types.UnicodeListType, 'Argument list')),
                         ('anv', A(types.DictType, 'Environment dictionary')),
                         ('pathLookUp', A(types.BooleanType, 'Search for program in $PATH')),
                         ('bindstdinout', A(types.BooleanType, 'Redirect stdin, stdout and stderr of child')),
                         ('bindpty', A(types.BooleanType, 'Redirect stdin, stdout and stderr of child to a pty')),
                         ('preExec', A(types.FunctionType, 'Function to run in child prior to exec'))],
                        2),
                     'Start a process')

    class process_user(Grimoire.Performer.SubMethod):
        __path__ = ['process', '$processservername']
        def _call(self, path, binary, args = [], env = None, pathLookUp = True, bindstdinout = True, bindpty = True, preExec = None):
            username, password, uid, gid, gecos, homeDir, shell = pwdentry = pwd.getpwnam(path[-1])
            def newPreExec():
                preExec and preExec()
                os.setreuid(uid, uid)
                os.setregid(gid, gid)
                os.setsid()
                os.chdir(homeDir)
                os.umask(0)
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, path=['process', '$processservername']
                                      )(binary, args, env, pathLookUp, bindstdinout, bindpty, newPreExec))

        __dir_allowall__ = False
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, 1,
                                      ['list', 'users', '$processservername'] + path)(depth))

        def _params(self, path):
            params = Grimoire.Types.getValue(
                self._callWithUnlockedTree(
                    lambda: self._getpath(Grimoire.Types.TreeRoot,
                                          path = ['introspection', 'params'] + self._physicalGetpath(Grimoire.Types.MethodBase,
                                                                                                     path=['process', '$processservername'])._pathForSelf()
                                          )()))
            return A(params,
                     Grimoire.Types.Formattable(
                         'Start a process for user %(user)s',
                         user=Grimoire.Types.GrimoirePath(path)))
