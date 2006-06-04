#! /usr/bin/env python

if __name__ == '__main__':
    import Grimoire, sys
    sys.exit(Grimoire._.clients.cli(sys.argv[1:]))
else:
    import Grimoire.Performer, Grimoire.Utils, Grimoire.Types, string, sys, types

    class Performer(Grimoire.Performer.Base):
        class cli(Grimoire.Performer.Method):
            def _call(self, expressions = [], stdin = sys.stdin, stdout = sys.stdout, stderr = sys.stderr):
                # Some magic :)
                if map(string.lower, expressions) == ['--help']:
                    stderr.write(unicode(self._params()) + '\n')
                    return 0
                
                Session = self._getpath(Grimoire.Types.MethodBase).base()
                class CliSession(Session):
                    sessionPath = Session.sessionPath + ['cli']

                exprs = expressions[1:] or self._getpath(
                    Grimoire.Types.TreeRoot,
                    path = ['directory', 'get'] + CliSession.sessionPath
                    )(['defaultcommands'], [], False)
                
                try:
                    result = CliSession((expressions and expressions[0]) or None)
                except Exception:
                    import traceback
                    traceback.print_exc()
                    return 1

                res = Grimoire.Types.getValue(result)

                if not Grimoire.Utils.isInstance(res, CliSession):
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
                    if exprs and exprs != ['']:
                        for expr in exprs:
                            result = sess.eval(expr)
                            if not result.error:
                                stderr.write(unicode(result.result) + '\n')
                            elif result.error == ExitCli:
                                raise ExitCli
                            else:
                                stderr.write(unicode(result.error) + '\n')
                    else:
                        while 1:
                            stdout.write(Grimoire.Utils.encode('> '))
                            cmd = stdin.readline()[:-1]
                            if not cmd:
                                raise ExitCli
                            result = sess.eval(cmd)
                            if not result.error:
                                stderr.write(unicode(result.result) + '\n')
                            elif result.error == ExitCli:
                                raise ExitCli
                            else:
                                stderr.write(unicode(result.error) + '\n')
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
