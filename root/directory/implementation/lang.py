import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, os, re, ConfigParser

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

langs = None
def getLangs(directory):
    global langs
    if langs is None:
        f = os.popen('locale -a')
        # FIXME: Yes, all Linuxes are broken, and the listing from
        # locale -a, aswell as the file locale.alias _is_ in
        # latin-1. Regardles of current locale and whatnot. Bah.
        locales = [line.strip().decode('latin-1') for line in f.xreadlines()]
        f.close()

        localespecre = re.compile('^[a-z][a-z]_[A-Z][A-Z].*$')
        localespecs = filter(lambda spec: localespecre.match(spec), locales)
        localenames = filter(lambda spec: not localespecre.match(spec), locales)

        try:
            f = file(directory.get.sysinfo(['files', 'languages', 'all_languages'], '/usr/share/locale/all_languages', False))
            langnames = ConfigParser.ConfigParser()
            langnames.readfp(f)
            f.close()

            def nameoflocale(localespec):
                langspec = localespec.split('.', 1)[0].split('@', 1)[0]
                if '_' in langspec:
                    lang, region = langspec.split('_')
                    pairs = [(langspec, 'name[' + langspec + ']'),
                             (langspec, 'name[' + lang + ']'),
                             (langspec, 'name'),
                             (lang, 'name[' + langspec + ']'),
                             (lang, 'name[' + lang + ']'),
                             (lang, 'name')]
                else:
                    pairs = [(langspec, 'name[' + langspec + ']'),
                             (langspec, 'name')]
                for (section, option) in pairs:
                    try:
                        return langnames.get(section, option).decode()
                    except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
                        pass
                return localespec
            langs = dict([(nameoflocale(localespec), localespec)
                          for localespec in localespecs])
        except IOError:
            langs = dict([(name, name) for name in localenames])
    return langs

sortedlangs = None
def getSortedLangs(directory):
    global sortedlangs
    if sortedlangs is None:
        sortedlangs = getLangs(directory).items()
        sortedlangs.sort(lambda (x1, y1), (x2, y2): cmp(x1, x2))
    return sortedlangs

class Performer(Grimoire.Performer.Base):
    class get_sysinfo(Grimoire.Performer.SubMethod):
        def _call(self, path):
            def unlocked(self, path):
                if not path or path[0] != Grimoire.Types.pathSeparator:
                    raise AttributeError(path)
                path = path[1:]
                if path == ['languages', 'dict']:
                    return getLangs(self._getpath(Grimoire.Types.MethodBase, 1))
                elif path == ['languages', 'sorted']:
                    return getSortedLangs(self._getpath(Grimoire.Types.MethodBase, 1))
                raise AttributeError(path)
            return self._callWithUnlockedTree(unlocked, self, path)
        def _params(self, path):
            return A(Ps(),
                     Grimoire.Types.Formattable(
                         'Read the %(attribute)s of the system',
                         Types.Reducible(path[1:], ' ')))
        def _dir(self, path, depth):
            if not depth:
                if (not path or
                    path[0] != Grimoire.Types.pathSeparator):
                    return []
                try:
                    self._call(path)
                    return [(1, [])]
                except AttributeError:
                    return []
            # FIXME: Not quite implemented yet, huh?
            return []
