import Grimoire.Utils, Grimoire.Performer, Grimoire.Types, types, cyruslib, managesieve

class Performer(Grimoire.Performer.Base):
    class maildir_user(Grimoire.Performer.SubMethod):
        __related_group__ = ['directory']
        __path__ = ['maildir', 'user', '$cyrusservername']
        def _call(self, path, name, uid = None, gid = None, **variables):
            getParam = self._getpath(Grimoire.Types.TreeRoot
                                     ).directory.get.parameters

            conn = getParam([ 'local', 'cyrus', 'conn'], cache=True)
            conn.cm('user', name)

            rHost = getParam(['local', 'cyrus', 'server', 'host'], None)
            rPort = getParam(['local', 'cyrus', 'server', 'port'], None)
            rCyrusUsername = getParam(['local', 'cyrus', 'username'], 'cyrus')
            rCyrusPassword = getParam(['local', 'cyrus', 'password'], None)

            connParams = {}
            if rHost is not None: connParams['host'] = rHost
            if rPort is not None: connParams['port'] = rPort

            sieveconn = managesieve.MANAGESIEVE(**connParams)
            res = sieveconn.login(name, rCyrusUsername, rCyrusPassword)
            if res != 'OK': raise Exception(res)

            sieveconn.putscript('kolab-deliver.siv', """
            
require "fileinto";
if anyof(not header :contains ["X-Kolab-Scheduling-Message"] [""],
             header :contains ["X-Kolab-Scheduling-Message"] ["FALSE"]) {
 fileinto "INBOX/Inbox";
}

            """)
            sieveconn.logout()

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
        def _call(self, path, name, gid = None, **variables):
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

    class maildir_group(Grimoire.Performer.SubMethod):
        __related_group__ = ['directory']
        __path__ = ['maildir', 'group', '$cyrusservername']
        def _call(self, path, name, gid = None, **variables):
            conn = self._getpath(Grimoire.Types.TreeRoot
                                 ).directory.get.parameters([ 'local', 'cyrus', 'conn'], cache=True)
            
            conn.cm('shared', conn.sep.join(path + [name]))

            #### fixme ####
            # description = """Change this to only allow the group
            # itself access as soon as we have working ptloader
            # (libnss support) in cyrus!"""
            #### end ####
            
            conn.sam('shared', conn.sep.join(path + [name]), 'anyone', 'lrswipcda')


            return Grimoire.Types.AnnotatedValue(
                None,
                'Successfully created group maildir')

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
                                                    'Numerical group ID')),
                     ],
                    1),
                Grimoire.Types.Formattable(
                    'Create a new mailgroup-directory in %(group)s',
                    group=Grimoire.Types.LocalPath(path)))
