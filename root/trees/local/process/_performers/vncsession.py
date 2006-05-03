import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, types, pwd, grp, socket, os, pty

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive


class Performer(Grimoire.Performer.Base):
    class create_vncsession(Grimoire.Performer.SubMethod):
        __path__ = ['create', 'vncsession', '$processservername']
        __related_group__ = ['user']
        def _related(self, *arg, **kw):
            return Grimoire.Performer.SubMethod._related(self, *arg, **kw)
        def _call(self, path):
            pid, childstdin, childstdout, childstderr = self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase,
                                      path = ['create', 'process', '$processservername'] + path
                                      )('vncserver', ['vncserver'], bindpty=False))
            output = childstdout.readlines()
            childstdin.close()
            childstdout.close()
            childstderr.close()
            status = os.waitpid(pid, 0)[1]
            if status != 0:
                raise Exception(''.join(output))
            displayname = None
            for line in output:
                if ' desktop is ' in line:
                    displayname = line[:-1].split(' ')[-1]
            if displayname is None:
                raise Exception(''.join(output))
            return A(displayname,
                     'New VNC server session created with display name')
        
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase,
                                      path = ['list', 'users', '$processservername'] + path)(depth))

        def _params(self, path):
            return A(Ps([]),
                     Grimoire.Types.Formattable(
                         'Start a new vnc server for user %(user)s',
                         user=Grimoire.Types.GrimoirePath(path)))

    class delete_vncsession(Grimoire.Performer.SubMethod):
        __path__ = ['delete', 'vncsession', '$processservername']
        __related_group__ = ['vncsession']
        def _call(self, path):
            pid, = self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase,
                                      path = ['create', 'process', '$processservername'] + path[:-1]
                                      )('vncserver', ['vncserver', '-kill', ':' + path[-1]],
                                        bindstdinout=False, bindpty=False))
            if os.waitpid(pid, 0)[1] != 0:
                raise Exception('Unable to remove session. Please contact your local server administrator')
            return A(None,
                     'VNC session successfully removed')
            
        def _dir(self, path, depth):
            def unlocked():
                def extendfn((leaf, path), prefix, depth):
                    if not leaf:
                        return []
                    hostname = socket.gethostname()
                    hostnamelenplusone = len(hostname) + 1 # account for separating ':'
                    def filter(file):
                        if not file.startswith(hostname):
                            raise Grimoire.Utils.FilterOutError
                        id = file[hostnamelenplusone:]
                        if '.' in id:
                            raise Grimoire.Utils.FilterOutError
                        return (1, Grimoire.Utils.removePrefix(prefix, [id]))
                    vncpath = unicode(Grimoire.Types.LocalPath(pwd.getpwnam(path[-1])[5]) + '.vnc')
                    try:
                        dirlist = os.listdir(vncpath)
                    except:
                        dirlist = []
                    return Grimoire.Utils.Map(filter, dirlist)
                return Grimoire.Performer.DirListExtender(
                    path, depth,
                    lambda prefix, depth: self._getpath(Grimoire.Types.MethodBase,
                                                        path = ['list', 'users', '$processservername'] + prefix)(depth),
                    extendfn)
            return self._callWithUnlockedTree(unlocked)

        def _params(self, path):
            return A(Ps([]),
                     Grimoire.Types.Formattable(
                         'End VNC session %(session)s for %(user)s',
                         session=path[-1],
                         user=Grimoire.Types.GrimoirePath(path[:-1])))


