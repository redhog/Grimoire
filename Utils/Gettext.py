import gettext, Fn
from Grimoire.Utils.Types import Gettext

class NullTranslations(gettext.NullTranslations):
    def gettext(self, message):
        if self._fallback:
            return self._fallback.gettext(message)
        raise Gettext.UntranslatableError()

    def ngettext(self, msgid1, msgid2, n):
        if self._fallback:
            return self._fallback.ngettext(msgid1, msgid2, n)
        raise Gettext.UntranslatableError()

    def ugettext(self, message):
        if self._fallback:
            return self._fallback.ugettext(message)
        raise Gettext.UntranslatableError()

    def ungettext(self, msgid1, msgid2, n):
        if self._fallback:
            return self._fallback.ungettext(msgid1, msgid2, n)
        raise Gettext.UntranslatableError()

class GNUTranslations(gettext.GNUTranslations, NullTranslations):
    def __init__(self, *arg, **kw):
        gettext.GNUTranslations.__init__(self, *arg, **kw)
        self._catalog[''] = ''
        
    def gettext(self, message):
        try:
            tmsg = self._catalog[message]
            # Encode the Unicode tmsg back to an 8-bit string, if possible
            if self._charset:
                return tmsg.encode(self._charset)
            return tmsg
        except KeyError:
            return NullTranslations.gettext(self, message)

    def ngettext(self, msgid1, msgid2, n):
        try:
            tmsg = self._catalog[(msgid1, self.plural(n))]
            if self._charset:
                return tmsg.encode(self._charset)
            return tmsg
        except KeyError:
            return NullTranslations.ngettext(self, msgid1, msgid2, n)

    def ugettext(self, message):
        try:
            return self._catalog[message]
        except KeyError:
            return NullTranslations.ugettext(self, message)

    def ungettext(self, msgid1, msgid2, n):
        try:
            return self._catalog[(msgid1, self.plural(n))]
        except KeyError:
            return NullTranslations.ungettext(self, msgid1, msgid2, n)

def translation(domain, localedir=None, languages=None,
                class_=GNUTranslations, fallback=False):
    try:
        res = gettext.translation(domain, localedir, languages, class_)
        if fallback:
            res.add_fallback(fallback)
        return res
    except IOError, e:
        if fallback:
            return fallback
        else:
            raise e

class Translations:
    def __init__(self, localedir = None, domain = None, fallback = None):
        self.__localedir = localedir
        self.__domain = domain
        self.__fallback = fallback

    def __call__(self, languages):
        try:
            return translation(self.__domain,
                               self.__localedir,
                               languages,
                               fallback = self.__fallback and self.__fallback(languages) or None)
        except Exception, e:
            return NullTranslations()
    __call__ = Fn.cachingFunction(__call__)

nullTranslations = Translations()
