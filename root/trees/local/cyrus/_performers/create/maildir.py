import Grimoire.Utils, Grimoire.Performer, Grimoire.Types, types, cyruslib

class Performer(Grimoire.Performer.Base):
    class maildir_user(Grimoire.Performer.SubMethod):
        __related_group__ = ['directory']
        __path__ = ['maildir', 'user', '$cyrusservername']
        def _call(self, path, name, uid = None, gid = None, **variables):
            conn = self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters([ 'local', 'cyrus', 'conn'], cache=True)
            
            conn.cm('user', name)

            return Grimoire.Types.AnnotatedValue(
                None,
                'Successfully created maildir')

        def _dir(self, path, depth):
            return []
        
        def _params(self, path):
            return Grimoire.Types.AnnotatedValue(
                Grimoire.Types.ParamsType.derive(
                    [('name',
                      Grimoire.Types.AnnotatedValue(
                          types.UnicodeType,
                          "Name of copy to create")),
                     ('uid',
                      Grimoire.TypessrcPath.AnnotatedValue(types.IntType,
                                                    'Numerical user ID')),
                     ('gid',
                      Grimoire.Types.AnnotatedValue(types.IntType,
                                                    'Numerical user homegroup ID')),
                     ],
                    1),
                Grimoire.Types.Formattable(
                    'Create a new mail-directory in %(group)s',
                    group=Grimoire.Types.LocalPath(path)))

    class maildir_homegroup(Grimoire.Performer.SubMethod):
        __related_group__ = ['directory']
        __path__ = ['maildir', 'homegroup', '$cyrusservername']
        def _call(self, path, name, gid = None):
            return Grimoire.Types.AnnotatedValue(
                None,
                'Successfully created group directory')

        def _dir(self, path, depth):
            return []

        def _params(self, path):
            return Grimoire.Types.AnnotatedValue(
                Grimoire.Types.ParamsType.derive(
                    [('name',
                      Grimoire.Types.AnnotatedValue(
                          types.UnicodeType,
                          "Name of copy to create")),
                     ('gid',
                      Grimoire.Types.AnnotatedValue(types.IntType,
                                                    'Numerical user homegroup ID')),
                     ],
                    1),
                Grimoire.Types.Formattable(
                    'Create a new mailgroup-directory in %(group)s',
                    group=Grimoire.Types.LocalPath(path)))
