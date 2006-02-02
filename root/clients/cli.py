#! /usr/bin/env python

if __name__ == '__main__':
    import Grimoire, sys
    sys.exit(Grimoire._.clients.cli(sys.argv[1:]))
else:
    import Grimoire.Performer, Grimoire.Utils, Grimoire.Types, string, sys, types, traceback

    class Performer(Grimoire.Performer.Base):
        class cli(Grimoire.Performer.Method):
            def _call(self, expressions = [], stdin = sys.stdin, stdout = sys.stdout, stderr = sys.stderr):
                # Some magic :)
                if map(string.lower, expressions) == ['--help']:
                    stderr.write(unicode(self._params()) + '\n')
                    return 0

                treeExpr = (expressions and expressions[0]) or None
                exprs = expressions[1:] or self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(['clients', 'cli', 'defaultcommands'], [], False)

                try:
                    result = self._getpath(Grimoire.Types.MethodBase).base()(treeExpr)
                except Exception:
                    traceback.print_exc()
                    return 1

                res = Grimoire.Types.getValue(result)

                if not Grimoire.Utils.isInstance(res, self._getpath(Grimoire.Types.MethodBase).base()):
                    stdout.write(unicode(res) + '\n')
                    if exprs is not None:
                        stderr.write("Error: Tree expression did not return a tree.\n")
                        return 1
                    return 0

                comment = Grimoire.Types.getComment(result)
                if comment is not None:
                    stderr.write(unicode(comment) + '\n')
                sess = res

                res = 0

                class ExitCli(Exception): pass

                class Logout(Grimoire.Performer.Base):
                    class logout(Grimoire.Performer.Method):
                        def _call(self):
                            raise ExitCli()
                        def _params(self):
                            return A(Ps(), 'Really log out?')

                sess.insert([], Logout(), root = True, first = True)

                try:
                    for expr in self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(['clients', 'cli', 'initcommands'], [], False):
                        try:
                            stderr.write(unicode(sess.eval(expr)) + '\n')
                        except ExitCli, e:
                            raise e
                        except Exception, e:
                            traceback.print_exc()
                            res = 1

                    if exprs and exprs != ['']:
                        for expr in exprs:
                            try:
                                stdout.write(unicode(sess.eval(expr)) + '\n')
                            except ExitCli, e:
                                raise e
                            except Exception, e:
                                traceback.print_exc()
                                res = 1
                    else:
                        while 1:
                            stdout.write(Grimoire.Utils.encode('> '))
                            cmd = stdin.readline()[:-1]
                            if not cmd:
                                raise ExitCli()
                            try:
                                stdout.write(unicode(sess.eval(cmd)) + '\n')
                            except ExitCli, e:
                                raise e
                            except Exception, e:
                                traceback.print_exc()
                                res = 1
                except ExitCli:
                    stderr.write('You have been logged out. Good bye!\n')
                    pass
                return res

            def _params(self):
                return Grimoire.Types.AnnotatedValue(
                    Grimoire.Types.ParamsType.derive(
                        [('expressions', Grimoire.Types.AnnotatedValue(Grimoire.Types.ListType.derive(types.UnicodeType), 'Grimoire expressions to evaluate. The first one specifies a tree, within wich the rest are evaluated'))],
                        0),
                    'The command-line client accepts a "tree"-expression and any number of "normal" expressions. The tree expression is evaluated in the main Grimoire tree, and if it evaluates to a new Grimoire tree, the remaining normal expressions are evaluated in that tree. If no "normal" expressions are given, but instead a single extra argument being the empty string "", the command-line client will present the user with a prompt at which normal commands can be written and evaluated directly')
