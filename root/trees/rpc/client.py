import Grimoire.Performer, Grimoire.Utils.RPC, Grimoire.About, types, string, urllib, base64, threading, traceback

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

debugExistence = 0
debugCalls = 0

class Leaf:
    pass

class ClientPerformer(Grimoire.Performer.Physical):
    """Wraps an rpc binding up as a Gimoire tree, that is, as a
    Performer. The rpc binding object should have one method, call,
    with the signature (path, *arg, **kw), where path is the path to
    the method to invoke on the tree, and *arg and **kw are arguments
    to give the method.
    """
    __slots__ = ['_binding']

    def __init__(self, binding):
        Grimoire.Performer.Physical.__init__(self)
        self._binding = binding
        for about in Grimoire.Performer.Logical(self).introspection.about():
            Grimoire.About.addAbout(about)

    # Logical node API

    def _treeOp_recurse(self, path, treeOp, **kw):
        if debugCalls: print "Remote:    -> " + treeOp + ': ' + '.'.join(path), kw
        return self._binding.call(path=path, treeOp=treeOp, **kw)

class Performer(Grimoire.Performer.Base):
    class client(Grimoire.Performer.Method):
        def _call(self):
            return ClientPerformer
        def _params(self):
            return A(Ps(),
                     'A Grimoire tree object served over an rpc channel, such as SOAP, XML-rpc or DIRT, will need some client-side support to look like a real Grimoire tree to the client side application. Specifically, the internal functions of a Performer object mut be recreated uing the introspective (public) methods of the server tree. This method returns a class that implementing such client-side support')
