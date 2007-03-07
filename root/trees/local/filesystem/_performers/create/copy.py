import Grimoire.Utils, Grimoire.Performer, Grimoire.Types, types, os, stat, errno, StringIO

copyBufferSize = 1024

def manglePath(src, dst):
    return dst

def mangleFile(path):
    return open(unicode(path), 'r')

class Performer(Grimoire.Performer.Base):
    class copy(Grimoire.Performer.SubMethod):
        __related_group__ = ['directory']
        __path__ = ['copy', '$fileservername']
        def _call(self, path, name, source, uid = None, gid = None, manglePath = manglePath, mangleFile = mangleFile):
            testpath = ['introspection', 'able', 'read', 'copy'] + source
            if not self._getpath(Grimoire.Types.TreeRoot, path=testpath)(effective=True):
                raise AttributeError(testpath)

            base = Grimoire.Types.defaultLocalRoot + self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                ['local', 'filesystem', 'basepath'], []))

            srcRoot = source
            dstRoot = path + [name]
            
            def copytree(src, dst):
                dst = manglePath(src, dst)

                srcPathStr = unicode(base + srcRoot + src)
                dstPathStr = unicode(base + dstRoot + dst)

                statInfo = Grimoire.Utils.lstat(srcPathStr)

                dstUid = [uid, statInfo.st_uid][uid is None]
                dstGid = [gid, statInfo.st_gid][gid is None]

                ensurePath = dst
                if not stat.S_ISDIR(statInfo.st_mode) and ensurePath:
                    ensurePath = ensurePath[:-1]
                
                self._callWithUnlockedTree(
                    lambda: self._getpath(Grimoire.Types.MethodBase,
                                          path=['path', '$fileservername'] + dstRoot + ensurePath
                                          )(mode=stat.S_IMODE(statInfo.st_mode), uid=dstUid, gid=dstGid))

                if stat.S_ISREG(statInfo.st_mode):
                    srcFile = mangleFile(base + srcRoot + src)
                    dstFile = open(dstPathStr, 'w')
                    data = 1
                    while data:
                        data = srcFile.read(copyBufferSize)
                        dstFile.write(data)
                    srcFile.close()
                    dstFile.close()
                    os.chmod(dstPathStr, stat.S_IMODE(statInfo.st_mode))
                    Grimoire.Utils.lchown(dstPathStr, dstUid, dstGid)
                elif stat.S_ISDIR(statInfo.st_mode):
                    for name in os.listdir(srcPathStr):
                        copytree(src + [name], dst + [name])
            copytree([], [])
            return Grimoire.Types.AnnotatedValue(None,
                                                 'Copied')
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._physicalGetpath(Grimoire.Types.MethodBase,
                                              path=['directory', '$fileservername'] + path
                                              )._treeOp([], 'dir', depth=depth))

        def _params(self, path):
            return Grimoire.Types.AnnotatedValue(
                Grimoire.Types.ParamsType.derive(
                    [('name',
                      Grimoire.Types.AnnotatedValue(
                          types.UnicodeType,
                          "Name of copy to create")),
                     ('source',
                      Grimoire.Types.AnnotatedValue(
                          Grimoire.Types.StringListType,
                          "Source path")),
                     ('uid',
                      Grimoire.Types.AnnotatedValue(types.IntType,
                                                    'Numerical user ID')),
                     ('gid',
                      Grimoire.Types.AnnotatedValue(types.IntType,
                                                    'Numerical user homegroup ID')),
                     ],
                    2),
                Grimoire.Types.Formattable(
                    'Copy a file or directory to %(destination)s',
                    destination=Grimoire.Types.LocalPath(path)))

    class varReplaceCopy(Grimoire.Performer.SubMethod):
        __related_group__ = ['directory']
        __path__ = ['var replace copy', '$fileservername']
        def _call(self, path, name, source, uid = None, gid = None, manglePath = manglePath, **variables):
            root = Grimoire.Types.defaultLocalRoot + self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                    ['local', 'filesystem', 'basepath'], []))
            variablesPathStr = unicode(root + source + ['.instansiate_variables'])
            if os.access(variablesPathStr, os.F_OK):
                f = open(variablesPathStr, 'r')
                for origLine in f:
                    line = origLine.strip()
                    if line and not line.startswith('#'):
                        if not '=' in line:
                            raise Exception("Instansiation variable file '" + variablesPath + \
                                            "' contains erraneous line '" + origLine + \
                                            "' (line is not a comment, nor does it contain a = sign).")
                        name, value = line.split('=')
                        variables[name.strip()] = value.strip()
                f.close()
            def mangleFile(path):
                content = open(unicode(path), 'r').read()
                for key, value in variables.items():
                    content = content.replace('%' + key + '%', value)
                return StringIO.StringIO(content)
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, path=['copy'] + ['$fileservername'] + path
                                      )(name,
                                        source,
                                        uid = uid,
                                        gid = gid,
                                        manglePath = manglePath,
                                        mangleFile = mangleFile))
        
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._physicalGetpath(Grimoire.Types.MethodBase,
                                              path=['directory', '$fileservername'] + path
                                              )._treeOp([], 'dir', depth=depth))
        def _params(self, path):
            return Grimoire.Types.AnnotatedValue(
                Grimoire.Types.ParamsType.derive(
                    [('name',
                      Grimoire.Types.AnnotatedValue(
                          types.UnicodeType,
                          "Name of copy to create")),
                     ('source',
                      Grimoire.Types.AnnotatedValue(
                          Grimoire.Types.StringListType,
                          "Source path")),
                     ('uid',
                      Grimoire.Types.AnnotatedValue(types.IntType,
                                                    'Numerical user ID')),
                     ('gid',
                      Grimoire.Types.AnnotatedValue(types.IntType,
                                                    'Numerical user homegroup ID')),
                     ],
                    2),
                Grimoire.Types.Formattable(
                    'Create a new copy at %(destination)s and merge in values from the extra named parameters into the files',
                    destination=Grimoire.Types.LocalPath(path)))

    class skeldir(Grimoire.Performer.SubMethod):
        __related_group__ = ['directory']
        __path__ = ['copy from skeleton', '$fileservername']
        def _call(self, path, name, uid = None, gid = None, skel=['skel'], **variables):
            root = Grimoire.Types.defaultLocalRoot + self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                    ['local', 'filesystem', 'basepath'], []))
            dstPath = root + path
            srcPath = None
            for prefixPath in Grimoire.Utils.Prefixes(list(dstPath['relative'])):
                prefixPath = root + prefixPath + skel
                if os.access(unicode(prefixPath), os.F_OK):
                    srcPath = prefixPath
                    break
            if not srcPath:
                srcPath = root + ['etc'] + skel
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, path=['var replace copy'] + ['$fileservername'] + path
                                      )(name,
                                        list(srcPath['relative']),
                                        uid = uid,
                                        gid = gid,
                                        **variables))
        
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._physicalGetpath(Grimoire.Types.MethodBase,
                                              path=['directory', '$fileservername'] + path
                                              )._treeOp([], 'dir', depth=depth))
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
                     ('skel',
                      Grimoire.Types.AnnotatedValue(
                          Grimoire.Types.StringListType,
                          "Skeleton path")),
                     ],
                    2),
                Grimoire.Types.Formattable(
                    'Create a new copy of a skeleton directory at %(destination)s',
                    destination=Grimoire.Types.LocalPath(path)))
