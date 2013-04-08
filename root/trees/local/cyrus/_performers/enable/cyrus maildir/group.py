import Grimoire.Utils, Grimoire.Performer, Grimoire.Types, types, cyruslib

class Performer(Grimoire.Performer.Base):
    class group(Grimoire.Performer.SubMethod):
        __related_group__ = ['directory']
        __path__ = ['group', '$cyrusservername']
        def _call(self, path, name, owner):
            conn = self._getpath(Grimoire.Types.TreeRoot
                                 ).directory.get.parameters([ 'local', 'cyrus', 'conn'], cache=True)

            mailbox = conn.sep.join(path + [name])
            group = Grimoire.Utils.encode(Grimoire.Types.UNIXGroup(path + [name]),
                                          'utf-8')
            
            conn.cm('shared', mailbox)
            if not conn.sam('shared',
                            mailbox,
                            'anyone',
                            ''):
                raise Exception('Unable to set anyone ACL on group mail folder: shared/%s lrswipc' % mailbox)
            if not conn.sam('shared',
                            mailbox,
                            'group:' + group,
                            'lrswipc'):
                raise Exception('Unable to set group ACL on group mail folder: shared/%s group:%s lrswipc' % (mailbox, group))
            if not conn.sam('shared',
                            mailbox,
                            owner,
                            'lrswipcda'):
                raise Exception('Unable to set owner ACL on group mail folder')

            return Grimoire.Types.AnnotatedValue(
                None,
                'Successfully created group maildir')

        def _dir(self, path, depth):
            return [(1, 'foo')]

        def _params(self, path):
            return Grimoire.Types.AnnotatedValue(
                Grimoire.Types.ParamsType.derive(
                    [('name',
                      Grimoire.Types.AnnotatedValue(
                          types.UnicodeType,
                          "Name of group")),
                     ('owner',
                      Grimoire.Types.AnnotatedValue(
                          types.UnicodeType,
                          "Username of group owner")),
                     ],
                    2),
                Grimoire.Types.Formattable(
                    'Enable a shared IMAP directory for the group %(group)s',
                    group=Grimoire.Types.LocalPath(path)))
