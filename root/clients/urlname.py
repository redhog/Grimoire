import Grimoire.Performer, Grimoire.Types, string

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive


#FIXME: This code should be merged with Types.HtmlComposer sometime...
class Performer(Grimoire.Performer.Base):
    class urlname_method2name(Grimoire.Performer.Method):
        def _call(self, method):
            import urllib
            if method is None:
                return None
            return urllib.quote_plus(Grimoire.Utils.encode(string.join(('',) + tuple(method), '.')))
        def _params(self):
            return A(Ps([('method', Grimoire.Types.UnicodeListType)]),
                     'Encodes a Grimoire method path (a list of strings) as a string suitable for embedding in URLs')

    class urlname_name2method(Grimoire.Performer.Method):
        def _call(self, name):
            import urllib
            if name is None or name == 'default':
                return None
            return tuple(urllib.unquote_plus(name).decode().split('.')[1:])
        def _params(self):
            return A(Ps(),
                     'Decodes a string encoded by method2name')

