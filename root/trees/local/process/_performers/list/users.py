import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, types, pwd, grp

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive


class Performer(Grimoire.Performer.Base):
    class users(Grimoire.Performer.SubMethod):
        __path__ = ['users', '$processservername']
        def _call(self, path, depth = Grimoire.Performer.UnlimitedDepth):
            """This is a quick and dirty hack, ok?"""
            dpth = depth
            if dpth == -1:
                dpth = Grimoire.Performer.UnlimitedDepth
            return Grimoire.Performer.DirListFilter(
                path, depth, 
                [(1, list(Grimoire.Types.UNIXGroup(grp.getgrgid(user[3])[0]) + [user[0]]))
                 for user in pwd.getpwall()])
        def _dir(self, path, depth):
            return [(1, [])]
        def _params(self, path):
            return A(Ps([]),
                     Grimoire.Types.Formattable(
                         'List users entries under %(path)s',
                         path=Grimoire.Types.LocalPath(path)))
