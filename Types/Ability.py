"""An ability is a function from paths to allow/disallow, used by
Performer.Restrictor and other classes to control access to trees of
methods or information.
"""
import Grimoire.Utils, time, string

debugSorting = 0
debugCalls = 0

abilityCacheTimout = 60 * 10 # 10 minutes ought to be enougth for everyone.


class Simple(object):
    """A Simple ability matches a given path by a prefix (given to it
    when instanciating the class). If the prefix path really is a
    prefix of the path, or if it is equal to the path with a ['']
    appended to it, the path is allowed.
    """
    __slots__ = ['path', 'preparedPath']
    
    def __init__(self, path):
        self.path = string.join(path, '.')
        self.preparedPath = self.path + ['.', ''][not self.path]

    def __call__(self, other, isPrefixOnly = 0):
        return (other.path + '.' == self.path
                or self.isSupersetOf(other)
                or (isPrefixOnly
                    and self.isSubsetOf(other)))

    def __cmp__(self, other):
        """Simple abilities may be compared, and are compared as their
        paths are compared."""
        return cmp(self.path, other.path)

    def isSupersetOf(self, other):
        return other.preparedPath.startswith(self.preparedPath)

    def isSubsetOf(self, other):
        return self.preparedPath.startswith(other.preparedPath)
        
    def isDisjunct(self, other):
        return not self.preparedPath.startswith(other.preparedPath) and not other.preparedPath.startswith(self.preparedPath)

    def intersection(self, other):
        if self.preparedPath.startswith(other.preparedPath):
            r = self
        elif other.preparedPath.startswith(self.preparedPath):
            r = other
        else:
            raise ValueError('Intersection only implemented if non-empty')
        return r

    def __str__(self):
        return str(self.path)

    def __unicode__(self):
        return unicode(self.path)

class Category(object): pass
class Allow(Category): pass
class Deny(Category): pass
class Ignore(Category): pass


def printList(lst):
    # This is a debug-function. Do NOT use.
    return string.join(Grimoire.Utils.Map(lambda x: x[0].__name__ + ': ' + unicode(x[1]), lst), ', ')

def listCmp(x, y):
    """Note: this function reverses the sort, in addition to selecting
    only the Simple abilities as sorting keys.
    """
    return cmp(y[1], x[1])

class List(object):
    __slots__ = ['abilities', 'allIs']
    
    def __init__(self, abilities = [], allIs = None):
        """This ability represents an Ignoreset as defined in
        Documentation/Ability.lyx and uses the theorems from there to
        optimize the list, so that it can be searched in O(log(n)m)
        time (where n is len(abilities) and m is len(path)).
        """

        self.allIs = allIs

        if Grimoire.Utils.isInstance(abilities, List):
            # Convert subclasses to the current class.
            if self.allIs is None:
                self.allIs = abilities.allIs
            self.abilities = abilities.abilities
            return

        # disjunctAbilities is a list of sublists, each consisting of
        # one Allow, Deny or Ignore, preceeded by any number of
        # smaller, disjunct Ignores. Each sublist is, taken as a
        # whole, disjunct with any other sublist.

        def disjunctCmp(x, y):
            """Note: this function reverses the sort, in addition to
            selecting only the Simple abilities of the last pairs as
            sorting keys.
            """
            return cmp(y[-1][1], x[-1][1])

        def allDisjunct(set, list):
            for member in list:
                if not set[1].isDisjunct(member[1]):
                    return False
            return True

        def canonize(simple):
            policy = simple[0]
            path = simple[1]
            if not Grimoire.Utils.isSubclass(policy, Category):
                policy = (Deny, Allow)[policy == 0]
            if not Grimoire.Utils.isInstance(path, Simple):
                path = Simple(path)
            return (policy, path)

        disjunctAbilities = Grimoire.Utils.SortedList([], disjunctCmp)
        todo = list(Grimoire.Utils.Map(canonize, abilities))
        while todo:
            if debugSorting: print 'Todo: ' + printList(todo) + '\n    DisjunctAbilities: ' + string.join(map(printList, disjunctAbilities), '; ')
            
            ability = todo[0]
            todo[0:1] = []

            shades = []
            
            for shadepos in xrange(len(disjunctAbilities) - 1, -1, -1):
                if debugSorting: print '        Shades: ' + printList(shades)
                if debugSorting: print '            Shadepos: ' + printList([disjunctAbilities[shadepos][-1]])
                if allDisjunct(disjunctAbilities[shadepos][-1], shades):
                    if disjunctAbilities[shadepos][-1][1].isSupersetOf(ability[1]):
                        if debugSorting: print '            Shadepos superset of ability'
                        isDisjunct = False
                        for shadeshadepos in xrange(len(disjunctAbilities[shadepos]) - 2, -1, -1):
                            shade = disjunctAbilities[shadepos][shadeshadepos]
                            if shade[1].isSupersetOf(ability[1]):
                                isDisjunct = True
                                break
                            elif ability[1].isSupersetOf(shade[1]):
                                todo[0:0] = [(ability[0], shade[1])]
                                if disjunctAbilities[shadepos][-1][0] is Ignore:
                                    disjunctAbilities[shadepos][shadeshadepos:shadeshadepos+1] = []
                        if not isDisjunct:
                            if disjunctAbilities[shadepos][-1][0] is Ignore:
                                disjunctAbilities[shadepos][0:0] = [(Ignore, ability[1])]
                            ability = None
                            break

                    elif disjunctAbilities[shadepos][-1][1].isSubsetOf(ability[1]):
                        if debugSorting: print '            Shadepos subset of ability'
                        if disjunctAbilities[shadepos][-1][0] is ability[0]:
                            disjunctAbilities[shadepos:shadepos + 1] = []
                        else:
                            shades += [(Ignore, disjunctAbilities[shadepos][-1][1])]
                            todo[0:0] = map(lambda (c, s): (ability[0], s),
                                            disjunctAbilities[shadepos][:-1])
                            if disjunctAbilities[shadepos][-1][0] is Ignore:
                                disjunctAbilities[shadepos:shadepos + 1] = []

            if ability is not None:
                disjunctAbilities.insertSort(shades + [ability])

        if debugSorting: print 'DisjunctAbilities: ' + string.join(map(printList, disjunctAbilities), '; ')

        # Remove any overflowing Ignores
        for pos in xrange(len(disjunctAbilities) - 1, -1, -1):
            if disjunctAbilities[pos][-1][0] is Ignore:
                disjunctAbilities[pos:pos+1] = []

        if debugSorting: print 'DisjunctAbilities: ' + string.join(map(printList, disjunctAbilities), '; ')

        self.abilities = Grimoire.Utils.SortedList(list(Grimoire.Utils.Flatten(disjunctAbilities)),
                                                   listCmp)

        # Remove superflous ignores, stemming from
        # Allow: x.y.z; Ignore: x.y.z, Deny x and the like...
        pos = 0
        while pos < len(self.abilities) - 1:
            if self.abilities[pos + 1][1].isSubsetOf(self.abilities[pos][1]):
                # Note, this means the two are equal, since the list is sorted!
                if self.abilities[pos][0] == Ignore:
                    self.abilities[pos:pos+1] = []
                elif self.abilities[pos+1][0] == Ignore:
                    self.abilities[pos+1:pos+2] = []
            else:
                pos += 1
                
    def eval(self, path, isPrefixOnly = 0, *arg, **kw):
        if isPrefixOnly:
            if self.eval(path, 0, *arg, **kw) is Allow:
                return Allow
            path = Simple(path)
            pos = self.abilities.pos((None, path))
            if pos >= len(self.abilities):
                # If we end up at end-of-list, take off one.
                pos = len(self.abilities) - 1
            elif not self.abilities[pos][1](path, 1, *arg, **kw):
                # Else, if we don't have an exact match,
                # step down one to find the first prefix. 
                pos -= 1
            while pos >= 0 and self.abilities[pos][1](path, 1, *arg, **kw):
                if self.abilities[pos][0] is Allow:
                    return Allow
                pos -= 1
            return Ignore
        else:
            for path in Grimoire.Utils.Prefixes(path):
                path = Simple(path)
                pos = self.abilities.pos((None, path))
                if pos < len(self.abilities) and self.abilities[pos][1](path, 0, *arg, **kw):
                    return self.abilities[pos][0]
                elif pos > 0 and self.abilities[pos - 1][1](path, 0, *arg, **kw):
                    return self.abilities[pos - 1][0]
            return Ignore

    def __call__(self, path, *arg, **kw):
        if debugCalls: print "Ability(%s) -> %s" % (path, self.eval(path, *arg, **kw) == Allow)
        return self.eval(path, *arg, **kw) == Allow

    def append(self, other):
        allIs = None
        if not self.abilities or self.allIs == other.allIs:
            allIs = other.allIs
        if not other.abilities:
            allIs = self.allIs
        return Grimoire.Utils.classOfInstance(self)(self.abilities + other.abilities, allIs)

    def prepend(self, other):
        allIs = None
        if not self.abilities or self.allIs == other.allIs:
            allIs = other.allIs
        if not other.abilities:
            allIs = self.allIs
        return Grimoire.Utils.classOfInstance(self)(other.abilities + self.abilities, allIs)

    def partition(self):
        """Divides the list into a pair of one list of only allows and
        ignores, and one list of only denies and ignores. The two
        lists will have their allIs attribute set to Allow respective
        Deny, meaning the allIs* methods will work on them."""

        def remove(abilities, what):
            """Removes either denies or allows, inserting ignores
            cutting away the same chunks of the other entries.

            Most general last
            foo.bar.fie, foo.bar, foo
            abilities .. done .. result
            """
            result = []
            while abilities:
                if abilities[-1][0] is what:
                    done = []
                    while result:
                        if not result[0][1].isDisjunct(abilities[-1][1]):
                            done.append((Ignore, result[0][1].intersection(abilities[-1][1])))
                        done.append(result[0])
                        result = result[1:]
                    result = done
                else:
                    result[0:0] = [abilities[-1]]
                abilities = abilities[:-1]
            return result

        klass = Grimoire.Utils.classOfInstance(self)
        return (klass(remove(self.abilities, Deny), Allow),
                klass(remove(self.abilities, Allow), Deny))

    def __union_intersection(self, other, union):
        """Let A,B denote the allow and deny partitions of a list. We
        then define union of lists in terms of normal set union and
        intersection (which is well-defined on a set with only either
        allow and ignore or deny (interpreted as "in the set", as
        allow) and ignore) as
        
        A1,A2 union B1,B2 <=> A1 union B1, A2 intersection B2
        
        and intersection of lists as
        
        A1,A2 intersection B1,B2 <=> A1 intersection B1, A2 union B2

        Note that these definitions conserves the normal (set
        theoretic) properties with respect to inverse (as defined for
        lists).
        """
        if union:
            own1, own2 = self.partition()
            others1, others2 = other.partition()
        else:
            own2, own1 = self.partition()
            others2, others1 = other.partition()

        # Union of the two first partitions, and the intersection of
        # the second partitions, that is, the inverse of the union
        # between their inverses.
        return own1.append(others1).append(
            own2.allIsSetInverse().append(
               others2.allIsSetInverse()).allIsSetInverse())
    
    def inverse(self):
        """Returns the inverse of this ignore-set. Everything allowed
        by this ignoreset is denied by the new one, everything denied
        by this one is allowed by the new one, and everything neither
        allowed not denied by this one is neither allowed nor denied
        by the new one."""
        def invert(pair):
            if pair[0] is Allow:
                return (Deny, pair[1])
            elif pair[0] is Deny:
                return (Allow, pair[1])
            return (Ignore, pair[1])
        allows, denies = self.partition()
        return Grimoire.Utils.classOfInstance(self)(
            map(invert, denies.abilities + allows.abilities))

    def union(self, other):
        return self.__union_intersection(other, True)
    
    def intersection(self, other):
        return self.__union_intersection(other, False)

    def minus(self, other):
        return self.intersection(other.inverse())

    def allIsSetInverse(self):
        """Takes the set inverses of the implied allowed or denied
        set of a list with allIs set."""
        if not self.allIs:
            raise ValueError('allIs must be set and, the same for all arguments, for this method to work')
        klass = Grimoire.Utils.classOfInstance(self)
        return klass([(Ignore, Simple([]))] +
                     self.abilities +
                     [(Ignore, Simple([])), (self.allIs, Simple([]))],
                     self.allIs)

    def allIsSetUnion(self, other):
        """Takes the set union of the implied allowed or denied
        sets of two lists with allIs set."""
        if not self.allIs and self.allIs is other.allIs:
            raise ValueError('allIs must be set and, the same for all arguments, for this method to work')
        return self.append(other)

    def allIsSetIntersection(self, other):
        """Takes the set intersection between the implied allowed or denied
        sets of two lists with allIs set."""
        return self.allIsSetInverse().allIsSetUnion(other.allIsSetInverse()).allIsSetInverse()

    def allIsSetMinus(self, other):
        """Takes the set minus between the implied allowed or denied
        sets of two lists with allIs set."""
        return self.allIsSetIntersection(other.allIsSetInverse())

    def setInverse(self):
        """Takes the set inverses of the implied allowed and denied
        sets."""
        ownAllows, ownDenies = self.partition()
        return ownAllows.allIsSetInverse().append(ownDenies.allIsSetInverse())

    def setUnion(self, other):
        """Given thwo Ignoresets takes the set union between the
        two implied allowed and denied sets."""
        ownAllows, ownDenies = self.partition()
        othersAllows, othersDenies = other.partition()
        return ownAllows.allIsSetUnion(othersAllows).append(ownDenies.allIsSetUnion(othersDenies))

    def setIntersection(self, other):
        """Given thwo Ignoresets takes the set intersections between the
        two implied allowed and denied sets."""
        return self.setInverse().setUnion(other.setInverse()).setInverse()

    def setMinus(self, other):
        """Given thwo Ignoresets takes the set minus between the
        two implied allowed and denied sets."""
        return self.setIntersection(other.setInverse())

    def allow(self, source, filter = None):
        """Grants this list some of the abilities allowed by source,
        selected by filter. Filter should not contain any explicit
        denies."""
        sourceAllows, sourceDenies = source.partition()
        if filter is not None:
            filterAllows, filterDenies = filter.partition()
            if filterDenies.abilities:
                raise ValueError('Filter should not contain explicit denies')
            sourceAllows = sourceAllows.intersection(filterAllows)
        return self.prepend(sourceAllows)

    def cancelAllow(self, filter):
        """Revoke all allows specified by filter. Filter should not
        contain any explicit denies."""
        ownAllows, ownDenies = self.partition()
        filterAllows, filterDenies = filter.partition()
        if filterDenies.abilities:
            raise ValueError('Filter should not contain explicit denies')
        return ownAllows.allIsSetMinus(filterAllows).append(ownDenies)

    def deny(self, ability):
        """Deny this list some abilities specified by ability. Ability
        should not contain any explicit Allows."""
        abilityAllows, abilityDenies = ability.partition()
        if abilityAllows.abilities:
            raise ValueError('Ability should not contain explicit allows')
        return self.prepend(abilityDenies)

    def cancelDeny(self, filter):
        """Revoke all denies specified by filter. Filter should not
        contain any explicit allows."""
        ownAllows, ownDenies = self.partition()
        filterAllows, filterDenies = filter.partition()
        if filterAllows.abilities:
            raise ValueError('Filter should not contain explicit allows')
        return ownAllows.append(ownDenies.allIsSetMinus(filterDenies))

    def __str__(self):
        return '<List ' + ', '.join(Grimoire.Utils.Map(lambda x: str(x[0].__name__) + ': ' + str(x[1]),
                                                       self.abilities)) + u'>'

    def __unicode__(self):
        return u'<List ' + u', '.join(Grimoire.Utils.Map(lambda x: unicode(x[0].__name__) + u': ' + unicode(x[1]),
                                                         self.abilities)) + u'>'
    
class CachedAbility:
    """This class is a baseclass for ability classes that needs
    caching of abilities for a certain time. Ability objects are
    created with the genAbility method, and cleared after
    abilityCacheTimout seconds.
    """
    __slots__ = ['_abilityCache', '_abilityCacheTime']
    
    def __init__(self):
        self._abilityCache = None
        self._abilityCacheTime = time.time()

    def abilityCache(self):
        curTime = time.time()
        if not self._abilityCache or self._abilityCacheTime + abilityCacheTimout < curTime:
            self._abilityCache = self.genAbility()
            self._abilityCacheTime = curTime
        return self._abilityCache

    def __call__(self, path, *arg, **kw):
        return self.abilityCache()(path, *arg, **kw)

    def __str__(self):
        return str(self.abilityCache())

    def __unicode__(self):
        return unicode(self.abilityCache())
