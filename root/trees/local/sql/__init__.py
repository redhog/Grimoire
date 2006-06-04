import Grimoire.Performer, Grimoire.Types, types, string

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive


class Performer(Grimoire.Performer.Base):
    class sql(Grimoire.Performer.Method):
        def _call(self, userName, password, server = None, database = None, adminname = None, adminpwd = None):
            import Grimoire.root.trees.local.sql._Ability, pg
            directory = self._callWithUnlockedTree(self._getpath(Grimoire.Types.TreeRoot).directory.new)
            setParam = directory.directory.set.parameters
            getParam = directory.directory.get.parameters
            
            if server: setParam(['local', 'sql', 'server'], server)
            rServer = getParam(['local', 'sql', 'server'], 'sql')

            if database: setParam(['local', 'sql', 'database'], database)
            rDatabase = getParam(['local', 'sql', 'database'], 'postgres')

            if adminname: setParam(['local', 'sql', 'admin', 'name'], adminname)
            rAdminname = getParam(['local', 'sql', 'admin', 'name'], 'postgres')

            if adminpwd: setParam(['local', 'sql', 'admin', 'password'], adminpwd)
            try:
                rAdminpwd = getParam(['local', 'sql', 'admin', 'password'])
            except AttributeError:
                raise Exception('No valid SQL admin password supplied')

            # connect to database
            db = pg.DB(rDatabase, rServer, -1, None, None, rAdminname, rAdminpwd)

            setParam(['local', 'sql', 'db'], db)

            user_entry = db.query(
                """select "password", "id" from "users" where "username" = '%s'""" %
                userName).getresult()
            if len(user_entry) == 0 or (password != user_entry[0][0]):
                raise Exception('Bad username or password')

            setParam(['local', 'sql', 'user', 'name'], userName)
            setParam(['local', 'sql', 'user', 'id'], user_entry[0][1])

            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase).load.standardtree(
                    __name__ + '._performers',
                    None, None,
                    Grimoire.root.trees.local.sql._Ability.SqlList(
                        userName, db),
                    directory))

        def _params(self):
            return A(Ps([('userName',
                          A(types.StringType,
                            'User name')),
                         ('password',
                          A(Grimoire.Types.PasswordType,
                            'User password')),
                         ('server',
                          A(types.StringType,
                            'The database server to connect to')),
                         ('database',
                          A(types.StringType,
                            'The database to connect to')),
                         ('adminname',
                          A(types.StringType,
                            'The database administrator account')),
                         ('adminpwd',
                          A(types.StringType,
                            'The database administrators password'))]),
                     'Log in and return a manipulation tree for the sql database')
