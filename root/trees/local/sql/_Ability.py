"""This module implements abilities, such as the ones defined in the
Ability module, that takes their set of allowed paths from tables in
an SQL database."""

import Grimoire.Types.Ability, sys

# For exception debugging
debugException = 0 

class SqlAbility(Grimoire.Types.Ability.CachedAbility):
    """Base-class for all SQL-based ability-classes."""
    def __init__(self, username, conn):
        """conn is an sql connection, usertable and grouptable
        are names of these tables in the database, and username
        is the name of the user in the usertable'
        """
        self.username = username
        self.conn = conn
        Grimoire.Types.Ability.CachedAbility.__init__(self)

def groupMemberships(conn, username):
    """Returns a list of groups a user is a member of,
    sorted by their length, with the longest ones first.
    """
    groups =[]
    try:
        groups = conn.query(
            "select name from usergroups where id = (select usergroup from users where username = '%s')" % username
            ).getresult()
        # The "everybody" group is hard coded to be number 0. 
        everybodygroup = conn.query("select name from usergroups where id = 0").getresult()
        groups = [ group[0] for group in groups ] + [ everybodygroup[0][0] ]
        groups.sort(lambda x, y: len(y.split(',')) - len(x.split(',')))
    except Exception, e:
        if (debugException):
            print "exception!"
            print e
    return groups

def sqlEntryList(userorgroupflag, name, conn):
    # Get abilities for either group or user name 

    if userorgroupflag == "group":
        table = "groupabilities"
        idfield = "usergroup"
        nametable = "usergroups"
        namefield = "name"
    else:
        table =  "userabilities"
        idfield = "user"
        nametable = "users"
        namefield = "username"

    res = conn.query("select ability, type from %s where %s = (select id from %s where %s = '%s')" %
                     (table, idfield, nametable, namefield, name)).getresult()
    def filterAbilities(res, type, name):
        return [(type, p[0].split('.')) for p in filter(lambda x: x[1] == name, res)]
    rights = (filterAbilities(res, Grimoire.Types.Ability.Allow, 'abilityAllow') +
              filterAbilities(res, Grimoire.Types.Ability.Deny, 'abilityDeny') +
              filterAbilities(res, Grimoire.Types.Ability.Ignore, 'abilityIgnore'))
    rights.sort(lambda x, y: len(y[1]) - len(x[1]))
    return rights

class SqlEntryList(SqlAbility):
    """This ability acts as a list of Simple abilitys, all taken from
    an SQL table. In these attributes, the paths are represented as
    strings separated by a dot (.)

    The paths are sorted on their lengths with the longest ones first.
    """
    def genAbility(self):
        return Grimoire.Types.Ability.List(sqlEntryList(self.username, self.conn))

def sqlList(username, conn):
    groupabilities = reduce(lambda x, y: x + y,
                            [sqlEntryList("group", group, conn)
                             for group in
                             groupMemberships(conn, username)],
                            [])    
    userabilities = sqlEntryList("user", username, conn)
    return userabilities + groupabilities

class SqlList(SqlAbility):
    """This ability is the concatenation of a set of SqlEntryList:s,
    taken from 

    1. the users own entries in the user ability table,

    2. the entries in the group ability table for each group
       the user is a member of.
    """
    def genAbility(self):
        return Grimoire.Types.Ability.List(sqlList(self.username, self.conn))
