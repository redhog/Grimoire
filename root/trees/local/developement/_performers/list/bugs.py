import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, types, os

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive

class Performer(Grimoire.Performer.Base):
    class fixmedir(Grimoire.Performer.SubMethod):
        __path__ = ['fixmedir', '$fileservername']
        def _call(self, path, depth = Grimoire.Performer.UnlimitedDepth,
                  fixmesAreMethods = True, fieldsAreMethods = True, itemsAreMethods = True, itemFieldsAreMethods = True):
            fixmes = self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(['local', 'developement', 'fixmes'], cache=True))

            def listFields(prefix, path, fields):
                assert not (prefix and path)
                if not path:
                    return [(1, prefix + [key])
                            for key in fields
                            if key not in ('name', 'location')]
                elif len(path) == 1 and path[0] in fields:
                    return [(1, prefix)]
                return []

            def listItems(prefix, path, items):
                assert not (prefix and path)
                result = []
                if len(path) < 2:
                    for (file, line), item in items.iteritems():
                        if path:
                            if not path[0] == file: continue
                            if itemsAreMethods: result.append((1, prefix + [str(line)]))
                            if itemFieldsAreMethods: result.extend(listFields(prefix + [str(line)], [], item.fields))
                        else:
                            if itemsAreMethods: result.append((1, prefix + [file, str(line)]))
                            if itemFieldsAreMethods: result.extend(listFields(prefix + [file, str(line)], [], item.fields))
                    return result
                elif len(path) > 1 and (path[0], int(path[1])) in items:
                    if itemsAreMethods: result.append((1, []))
                    if itemFieldsAreMethods: result.extend(listFields([], path[2:], items[(path[0], int(path[1]))].fields))
                return result

            def listFixme(prefix, path, fixme):
                assert not (prefix and path)
                result = []
                if not path:
                    if fixmesAreMethods: result.append((1, prefix))
                    if fieldsAreMethods: result.extend(listFields(prefix + ['fields'], [], fixme.fields))
                    result.extend(listItems(prefix + ['items'], [], fixme.items))
                elif path[0] == 'fields':
                    if fieldsAreMethods: result.extend(listFields([], path[1:], fixme.fields))
                elif path[0] == 'items':
                    result.extend(listItems([], path[1:], fixme.items))
                return result
            
            def listFixmes(prefix, path, fixmes):
                assert not (prefix and path)
                if not path:
                    result = []
                    for name, fixme in fixmes.iteritems():
                        result.extend(listFixme(prefix + [name], path, fixme))
                    return result
                else:
                    return listFixme(prefix, path[1:], fixmes[path[0]])

            return Grimoire.Performer.DirListFilter(
                [], depth, listFixmes([], path, fixmes.fixmes))
            
        def _dir(self, path, depth):
            return self._call(path, depth)
        def _params(self, path):
            return A(Ps([('depth', A(types.IntType, "Listing depth")),
                         ('fixmesAreMethods', A(types.BooleanType, 'Fixmes themselves are listed as methods')),
                         ('fieldsAreMethods', A(types.BooleanType, 'Fixme fields are listed as methods')),
                         ('itemsAreMethods', A(types.BooleanType, 'Items are listed as methods')),
                         ('itemFieldsAreMethods', A(types.BooleanType, 'Item fields are listed as methods'))
                         ]),
                     Grimoire.Types.Formattable(
                         'List fixmes under %(path)s',
                         path=Grimoire.Types.GrimoirePath(path)))

    class fixmes(Grimoire.Performer.SubMethod):
        __path__ = ['fixmes', '$fileservername']
        __related_group__ = ['code', 'fixmes']
        __dir_allowall__ = False
        def _call(self, path):
            fixmes = self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(['local', 'developement', 'fixmes'], cache=True))
            if len(path) == 1:
                return Grimoire.Types.Lines(
                    *[A(value, key)
                      for key, value
                      in fixmes.fixmes[path[0]].fields.iteritems()
                      if key not in ('name', 'location')] +
                     [A(Grimoire.Types.Lines(
                            *[A(value, key)
                              for key, value
                              in item.fields.iteritems()
                              if key not in ('name', 'location')]),
                        Grimoire.Types.Formattable("%(file)s:%(line)s", file=file, line=line))
                      for (file, line), item
                      in fixmes.fixmes[path[0]].items.iteritems()])
            elif path[1] == 'fields':
                if len(path) == 2:
                    return Grimoire.Types.Lines(
                        *[A(value, key)
                          for key, value
                          in fixmes.fixmes[path[0]].fields.iteritems()
                          if key not in ('name', 'location')])
                elif len(path) == 3:
                    return fixmes.fixmes[path[0]].fields[path[2]]
            elif path[1] == 'items':
                if len(path) == 3:
                    return None
                elif len(path) == 4:
                    return Grimoire.Types.Lines(
                        *[A(value, key)
                          for key, value
                          in fixmes.fixmes[path[0]].items[(path[2], int(path[3]))].fields.iteritems()
                          if key not in ('name', 'location')])
                elif len(path) == 5:
                    return fixmes.fixmes[path[0]].items[(path[2], int(path[3]))].fields[path[4]]
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase, path=['fixmedir', '$fileservername'] + path)(
                    depth,
                    fixmesAreMethods = True, fieldsAreMethods = True, itemsAreMethods = True, itemFieldsAreMethods = True))
        def _params(self, path):
            return Ps()
