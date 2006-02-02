import Grimoire.Utils, Reader, Writer, Types, SocketServer, types, exceptions, copy, sys, string, traceback, threading, thread, __builtin__

debugExceptions = ()
dontDebugExceptions = (Grimoire.Utils.UntranslatableError,)
debugDispatch = 0
profileDispatch = '' # 'dispatchprof-'
profileRead = '' # 'readprof-'
debugCall = 0
debugResult = 0
debugWrite = 0
debugRead = 0
debugThreads = 0
debugClass = 0
debugObject = 0


if profileDispatch or profileRead:
    import hotshot

def exc_info():
    type, value = old_exc_info()[:2]
    if hasattr(value, 'backtrace'):
        return (type, value, value.backtrace)
    return old_exc_info()
old_exc_info = sys.exc_info
sys.exc_info = exc_info

class StreamServer(SocketServer.TCPServer):
    """A server similar to TCPServer, that can be fed any bound socket
    or socket-like structure (e.g. SSL socket)."""
    def __init__(self, socket, RequestHandlerClass = None):
        SocketServer.BaseServer.__init__(self, socket.getsockname(), RequestHandlerClass)
        self.socket = socket
        self.server_activate()
        
    def server_bind(self):
        pass

class ExceptionHandlingRequestHandler(SocketServer.StreamRequestHandler):
    """A RequestHandler very similar to StreamRequestHandler, except
    it handles exceptions in handle() correctly."""
    def handle(self):
        try:
            self.realHandle()
        finally:
            self.realFinish()
    def finish(self):
        pass
    def setup(self):
        self.realSetup()

    # Override these in subclasses
    def realHandle(self):
        raise NotImplemented
    def realSetup(self):
        self.request.setblocking(1)
        SocketServer.StreamRequestHandler.setup(self)
    def realFinish(self):
        SocketServer.StreamRequestHandler.finish(self)


class RPCMessage:
    def __init__(self, id):
        self.id = id
    def __parts__(self):
        return {'id': str(self.id)}
    def __str__(self):
        return "<" + str(self.__class__) + ": " + str(self.__parts__()) + ">"

class RPCCall(RPCMessage):
    def __init__(self, arg, kw, *rarg, **rkw):
        RPCMessage.__init__(self, *rarg, **rkw)
        self.arg = arg
        self.kw = kw        
    def __parts__(self):
        p = RPCMessage.__parts__(self)
        p.update({'arg': self.arg, 'kw':self.kw})
        return p

class RPCCallReturn(RPCMessage): pass

class RCPResult(RPCCallReturn):
    def __init__(self, value, *rarg, **rkw):
        RPCCallReturn.__init__(self, *rarg, **rkw)
        self.value = value
    def __parts__(self):
        p = RPCCallReturn.__parts__(self)
        p.update({'value': self.value})
        return p

class RPCException(RPCCallReturn):
    def __init__(self, exc, *rarg, **rkw):
        RPCCallReturn.__init__(self, *rarg, **rkw)
        self.exc = exc    
    def __parts__(self):
        p = RPCCallReturn.__parts__(self)
        p.update({'exc': self.exc})
        return p

class Binding:
    def __init__(self, rfile, wfile, extension, sock = None):
        self.wfile = wfile
        self.buffer = Reader.Buffer(sock or rfile)
        self.extension = extension
        self.writelock = threading.Lock()
        self.readlocks = {}
        self.res = {}
        self.err = None

    def start(self):
        th = threading.Thread(target = self.readerThread, name = 'Reader thread for %s' % self)
        if debugThreads: print "Starting reader thread %s" % th
        th.setDaemon(1)
        th.start()
        
    def join(self):
        if debugThreads: print "Joining reader thread"
        self.readerThread()

    def readerThread(self):
        unknown = Exception('Unknown exception in reader thread')
        reads = 0
        while 1:
            reads += 1
            try:
                try:
                    if profileRead:
                        print "Read:", reads
                        p = hotshot.Profile(profileRead + str(reads))
                        try:
                            msg = p.runcall(Reader.read, self.buffer)
                        finally:
                            p.close()
                    else:
                        msg = Reader.read(self.buffer)
                    self.err = None
                    if debugRead: print "Read", reads, ":", msg
                except:
                    self.err = sys.exc_value
                    raise sys.exc_type, sys.exc_value, sys.exc_traceback
                try:
                    if msg[0] == 'RPCCall':
                        th = threading.Thread(
                            target = self.dispatchThread,
                            args = (msg[1:],),
                            name = 'Dispatch handler for %s' % threading.currentThread().getName())
                        if debugThreads: print "Starting dispatch thread %s" % th
                        th.start()
                    elif msg[0] == 'RPCCallReturn':
                        self.res[msg[1]] = msg[2]
                        if debugThreads: print "Reader thread: Locking readlock", msg[1]
                        self.readlocks[msg[1]].acquire()
                        if debugThreads: print "Reader thread: Notifying readlock", msg[1]
                        self.readlocks[msg[1]].notify()
                        if debugThreads: print "Reader thread: Unlocking readlock", msg[1]
                        self.readlocks[msg[1]].release()
                        if debugThreads: print "Reader thread: Unlocked readlock", msg[1]
                    else:
                        raise IOError('Unknown rpc message type', msg)
                except:
                    self.err = sys.exc_value

            finally:
                if self.err:
                    if debugThreads: print "Reader thread: Notifying all readlocks"
                    for readlock in self.readlocks.values():
                        readlock.acquire()
                        readlock.notify()
                        readlock.release()
                    if debugThreads: print "Reader thread: Notifying all readlocks done"

    def write(self, msg):
        self.writelock.acquire()
        try:
            if debugWrite: print "Write:", msg
            Writer.write(self.wfile, Writer.contract(msg, self.extension.serialize))
            self.wfile.write('\n')
            self.wfile.flush()
        finally:
            self.writelock.release()

    def dispatchThread(self, msg, callindex = [0]):
        callindex[0] += 1
        def dispatchThread(msg, callindex):
            msg = Reader.extend(msg, self.extension.parse)
            if debugDispatch or profileDispatch: print "Dispatch " + str(callindex[0]) + ":", msg
            try:
                res = self.dispatch(*msg[1], **msg[2])
            except:
                exc_type, exc_value = sys.exc_info()[:2]
                e = exc_value or exc_type
                if Grimoire.Utils.isInstance(e, *debugExceptions) and not Grimoire.Utils.isInstance(e, *dontDebugExceptions):
                    traceback.print_exc()
                res = Types.RaiseException()
            self.write(('RPCCallReturn', msg[0], res))
        if profileDispatch:
            p = hotshot.Profile(profileDispatch + str(callindex[0]))
            p.runcall(dispatchThread, msg, callindex)
            p.close()
        else:
            dispatchThread(msg, callindex)
            
    def dispatch(self, *arg, **kw):
        raise NotImplemented

    def call(self, *arg, **kw):
        if debugCall: print "Call:", arg, kw
        id = thread.get_ident()
        if id not in self.readlocks:
            if debugThreads: print "Call: Making readlock for", id
            self.readlocks[id] = threading.Condition()
        if debugThreads: print "Call: Locking readlock for", id
        self.readlocks[id].acquire()
        if debugThreads: print "Call: Locked readlock for", id
        if self.err is not None:
            if debugThreads: print "Call: Releasing readlock for", id
            self.readlocks[id].release()
            if debugThreads: print "Call: Released readlock for", id
            raise self.err
        try:
            self.write(('RPCCall', id, arg, kw))
            while self.err is None and id not in self.res:
                if debugThreads: print "Call: Waiting on readlock for", id
                self.readlocks[id].wait()
                if debugThreads: print "Call: Waiting on readlock for", id, "done"
            res = self.res[id]
            del self.res[id]
            err = self.err
        finally:
            if debugThreads: print "Call: Releasing readlock for", id
            self.readlocks[id].release()
            if debugThreads: print "Call: Released readlock for", id
        if err:
            raise err
        res = Reader.extend(res, self.extension.parse)
        if debugResult: print "Result:", res
        return res


class BindingRequestHandler(ExceptionHandlingRequestHandler):
    rbufsize = -1
    wbufsize = -1
    def realSetup(self):
        ExceptionHandlingRequestHandler.realSetup(self)
        self.binding = self.server.binding(rfile = self.rfile, wfile = self.wfile, sock = self.connection)
        self.binding.setup(self)
    def realFinish(self):
        self.binding.finish(self)
        ExceptionHandlingRequestHandler.realFinish(self)
    def realHandle(self):
        threading.currentThread().setName(
            'Request handler thread for connection at %s from %s to %s' % (
                self.request.getsockname(), self.request.getpeername(), self.server))
        self.binding.join()

class BindingServer(SocketServer.ThreadingMixIn, StreamServer):
    def __init__(self, socket, binding):
        StreamServer.__init__(self, socket, BindingRequestHandler)
        self.binding = binding

def BindingClient(socket, binding):
    rfile = socket.makefile('r')
    wfile = socket.makefile('r')
    bnd = binding(rfile = rfile, wfile = wfile, sock = socket)
    bnd.start()
    return bnd

class ObjectMappedExtension:
    def __init__(self, objectMap):
        self.serializeMap = Grimoire.Utils.InstanceMap(dict(
            Grimoire.Utils.Map(lambda type: (type.type, (type.typeName, type.serialize)), objectMap)))
        self.parseMap = dict(Grimoire.Utils.Map(lambda type: (type.typeName, type.parse), objectMap))

    def serializeMapGet(self, obj):
        return self.serializeMap[obj]
    serializeMapGet = Grimoire.Utils.cachingFunction(serializeMapGet)

    def serialize(self, obj):
        try:
            serializer = self.serializeMapGet(obj)
            return Types.Extension(serializer[0], serializer[1](obj))
        except:
            return self.serialize(Types.RaiseException())

    def parse(self, typeName, data):
        try:
            parseFn = self.parseMap[typeName]
        except KeyError:
            parseFn = Types.Extension
        return parseFn(typeName, data)


class ObjectMappedBinding(Binding):
    def __init__(self, objectMap = [], *arg, **kw):
        Binding.__init__(self, extension = ObjectMappedExtension(objectMap), *arg, **kw)


class ShortClassTypeContext:
    def __init__(self):
        self.klassSpecToKlass = {}
        self.klassToKlassSpec = Grimoire.Utils.AnyMap()

class ShortClassTypeTypeType(types.TypeType):
    def __isInstance__(self, obj):
        return obj in self.context.klassToKlassSpec
    def __isSubclassOf__(self, obj):
        return obj is ObjectTypeType
    def __isSubclass__(self, obj):
        return obj is not ObjectTypeType

class ShortClassType:
    typeName = 'SType'

    def __init__(self, context):
        self.context = context
        class ShortClassTypeType(types.TypeType):
            __metaclass__ = ShortClassTypeTypeType
            context = self.context
        self.type = ShortClassTypeType

    def serialize(self, klass):
        return self.context.klassToKlassSpec[klass]

    def parse(self, typeName, klassSpec):
        return self.context.klassSpecToKlass[klassSpec]

class ClassTypeTypeType(types.TypeType):
    def __isInstance__(self, obj):
        if obj is ObjectTypeType:
            return False
        try:
            return obj is Grimoire.Utils.getpath(
                Grimoire.Utils.loadModule(obj.__module__),
                obj.__name__.split('.'))
        except Exception:
            return False
    def __isSubclassOf__(self, obj):
        t = type(obj)
        return t in (ObjectTypeTypeType, ShortClassTypeTypeType) 
    def __isSubclass__(self, obj):
        t = type(obj)
        return t not in (ObjectTypeTypeType, ShortClassTypeTypeType) 

class ClassTypeType(types.TypeType):
    __metaclass__ = ClassTypeTypeType

class ClassType:
    type = ClassTypeType
    typeName = 'Type'

    def __init__(self, ability = None, context = None):
        """ability controls which classes to deserialize. It should be
        a function taking lists describing classes as arguments and
        returning a boolean. ability may also be None, in which case
        everything is allowed.

        A class-specification-list is a list of strings, specifying
        first the module of the class, then the name of the
        class. E.g. ['foo', 'bar', 'fie', 'naja'] means the class naja
        in the module foo.bar.fie (or the class fie.naja in the module
        foo.bar, or the class bar.fie.naja in the module foo). A list
        prefixed by '/' means to only allow the class if it is a
        subclass of another, allowed class.
        """
        self.ability = ability or (lambda x: 1)
        self.context = context

    def serialize(self, klass):
        klassSpec = []
        try:
            for base in klass.__bases__:
                klassSpec.extend(self.serialize(base))
        except AttributeError:
            pass
        klassSpec.append(klass.__module__.split('.') + klass.__name__.split('.'))
        if debugClass: print "Serialize class", klass, "->", klassSpec
        if self.context:
            self.context.klassSpecToKlass[tuple(klassSpec[-1])] = klass
        return klassSpec

    def parse(self, typeName, klassSpec):
        def allowedTypeSpec(typeSpec):
            if self.ability(typeSpec):
                return 1
            if self.ability(['/'] + typeSpec):
                return 0
            return None
        def allowedKlassSpec(klass):
            for typeSpec in klass:
                if allowedTypeSpec(typeSpec):
                    return 1
            return 0
        def getKlass(typeSpec):
            for (module, klass) in Grimoire.Utils.PrefixesSuffixes(typeSpec):
                try:
                    return Grimoire.Utils.getpath(
                        Grimoire.Utils.loadModule(string.join(module, '.')),
                        klass)
                except ImportError:
                    pass
            raise AttributeError()
        unallowed = []
        for typeSpec in Grimoire.Utils.Reverse(klassSpec):
            allowed = allowedTypeSpec(typeSpec)
            if allowed is None:
                unallowed.append(typeSpec)
                continue
            try:
                klass = getKlass(typeSpec)
            except AttributeError:
                continue
            klassSpec = self.serialize(klass)

            # Backward-lookup the name of the class deserialized and
            # check it was really allowed (some objects are reachable
            # via several names, and only the ones they report
            # themselves via __name__ and __module__ are used for
            # security checks). If the path allowing this class begun
            # with '/', check that a base-class was allowed too.
            if not allowedKlassSpec(klassSpec) or (not allowed and not allowedKlassSpec(klassSpec[:-1])):
                unallowed.append(typeSpec)
                continue
            if self.context:
                self.context.klassToKlassSpec[klass] = tuple(klassSpec[-1])
            return klass
        raise Exception(klassSpec, unallowed, self.ability)

class ObjectTypeTypeType(types.TypeType):
    """Never, ever, try to _serialize_ this class, or an object of it,
    or you will die a horrible infinite death."""
    def __isSubclassOf__(self, obj):
        return False
    def __isSubclass__(self, obj):
        return True

class ObjectTypeType(types.TypeType):
    """If you try to serialize this one too. Muahehehe"""
    __metaclass__ = ObjectTypeTypeType

roots = []
for root in types.__dict__.itervalues():
    if type(root) is types.TypeType and root not in roots:
        roots.append(root)

def getRoots(klass):
    parenttypes = []
    for parenttype in roots:
        try:
            if type(parenttype) is not types.TupleType and issubclass(klass, parenttype):
                parenttypes.append(parenttype)
        except Exception:
            pass
    return parenttypes

def castToRoots(obj):
    rootObjs = []
    for root in getRoots(Grimoire.Utils.classOfInstance(obj)):
        try:
            rootObjs.append(root(obj))
        except Exception:
            pass
    return rootObjs

class ObjectType:
    typeName = 'Object'
    type = ObjectTypeType

    def serialize(self, obj):
        def serialize():
            klass = Grimoire.Utils.classOfInstance(obj)
            dict = obj.__dict__
            # This is an ugglyhack workaround for types inheriting
            # from a built -in type.
            removedict = '__dict__' in dict and type(dict['__dict__']) is types.GetsetDescriptor
            removeweakref = '__weakref__' in dict
            if removedict or removeweakref:
                dict = {}
                dict.update(obj.__dict__)
            if removedict:
                del dict['__dict__']
            if removeweakref:
                del dict['__weakref__']
            
            if issubclass(klass, types.TypeType):
                return (klass, (obj.__name__, obj.__bases__, dict))
            elif issubclass(Grimoire.Utils.classOfInstance(klass), types.TypeType):
                return (klass, (castToRoots(obj), dict))
            else:
                return (klass, dict)

        if debugObject:
            print "Serialize object", Grimoire.Utils.objInfo(obj),
        res = serialize()
        if debugObject:
            print "-->", res
        return res

    def parse(self, typeName, (klass, members)):
        if issubclass(klass, types.TypeType):
            return klass(*members)
        if issubclass(Grimoire.Utils.classOfInstance(klass), types.TypeType):
            parentobjs, members = members
            parenttype = (parentobjs and type(parentobjs[0])) or object
            res = parenttype.__new__(klass, *parentobjs)
            parenttype.__init__(res, *parentobjs)
        else:
            class Tmp: pass
            res = Tmp()
            res.__class__ = klass
        res.__dict__.update(members)
        return res

class RaiseExceptionType:
    typeName = 'RaiseException'
    type = Types.RaiseException

    def serialize(self, obj):
        return (obj.exc_type, obj.exc_value, obj.exc_traceback)

    def parse(self, typeName, (exc_type, exc_value, exc_traceback)):
        # Would be cool if we could inject the pre-formatted
        # traceback, but I don't know how that could be done in
        # today's python... :(
        raise exc_type, exc_value

class NormalizedIterType:
    typeName = 'NormalizedIter'
    type = Grimoire.Utils.NormalizedIter

    def serialize(self, obj):
        return list(obj)

    def parse(self, typeName, obj):
        return obj

class ServerObjectType:
    typeName = 'ServerObject'
    type = Grimoire.Utils.RPC.ServerObject

    def __init__(self, binding):
        self.binding = binding

    def serialize(self, obj):
        return obj._getServerObjectId(self.binding)

    def parse(self, typeName, id):
        return self.binding.new(id)

# Ugglyhack to work around that python puts all types in
# __builtin__ instaed of in types...
def computeBuiltinTypes():
    builtinTypes = []
    for name, value in __builtin__.__dict__.iteritems():
        if (   value in types.__dict__.itervalues()
            or value in exceptions.__dict__.itervalues()):
            builtinTypes.append(name)
    return map(lambda x: ['__builtin__', x], builtinTypes)
builtinTypes = computeBuiltinTypes()

def stdObjectMap(binding = None, ability = None):
    def allowExceptionsTypes(path):
        return (   Grimoire.Utils.isPrefix(['exceptions'], path)
                or Grimoire.Utils.isPrefix(['types'], path)
                or Grimoire.Utils.isPrefix(['Grimoire', 'Utils', 'Types'], path)
                or path in builtinTypes
                or ability(path))
    ab = ability and allowExceptionsTypes
    res = []
    if binding:
        res += [ServerObjectType(binding)]
    context = ShortClassTypeContext()
    res += [NormalizedIterType(),
            RaiseExceptionType(),
            ShortClassType(context),
            ClassType(ab, context),
            ObjectType()]
    return res

class StdObjectMappedBinding(ObjectMappedBinding):
    def __init__(self, objectMap = [], ability = None, *arg, **kw):
        ObjectMappedBinding.__init__(
            self, objectMap + stdObjectMap(binding = self, ability = ability), *arg, **kw)
    def registerObject(self, obj):
        raise NotImplemented
    def new(self, id):
        raise NotImplemented
