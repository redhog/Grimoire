import Grimoire.Utils, Grimoire.Performer, Grimoire.Types, types, cyruslib

class Performer(Grimoire.Performer.Base):
    class user(Grimoire.Performer.SubMethod):
        __related_group__ = ['directory']
        __path__ = ['user', '$cyrusservername']
        def _call(self, path, name):
            conn = self._getpath(Grimoire.Types.TreeRoot
                                 ).directory.get.parameters([ 'local', 'cyrus', 'conn'], cache=True)
            
            if not conn.sam('user',
                            name,
                            name,
                            ''):
                raise Exception('Unable to set ACL onmail folder: user/%s' % name)
            
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
                          "Name of user")),
                     ],
                    1),
                Grimoire.Types.Formattable(
                    'Disable the IMAP directory for a user in the group %(group)s',
                    group=Grimoire.Types.LocalPath(path)))
