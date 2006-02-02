import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, string, pwd

class UidSubMethod(Grimoire.Performer.SubMethod):
    def _dir(self, path, depth):
        # FIXME: Not quite implemented yet, huh?
        return []

class Performer(Grimoire.Performer.Base):
    class get_userinfo(Grimoire.Performer.SubMethod):
        __path__ = ['get', 'userinfo', '$fileservername']
        def _call(self, path):
            if len(path) != 2 or path[0] != Grimoire.Types.pathSeparator:
                raise AttributeError(path)
            return list(pwd.getpwnam(path[1]))
        def _params(self, path):
            return A(Ps(),
                     Grimoire.Types.Formattable(
                         'Read the %(attribute)s of the current user',
                         Types.Reducible(path[1:], ' ')))
        __dir_allowall__ = False
        def _dir(self, path, depth):
            plen = len(path)
            if plen >= 2:
                depth = 0
            if not depth:
                 try:
                     self._call(path)
                     return [(1, [])]
                 except KeyError:
                     return []
            entries = Grimoire.Utils.Map(lambda (pw_name, pw_passwd, pw_uid, pw_gid, pw_gecos, pw_dir, pw_shell): [pw_name], pwd.getpwall())
            if plen == 0:
                entries = Grimoire.Utils.Map(lambda x: [Grimoire.Types.pathSeparator] + x, entries)
            return Grimoire.Utils.Map(lambda x: (1, x), entries)
