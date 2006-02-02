import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, string, os

class Performer(Grimoire.Performer.Base):
    class printers(Grimoire.Performer.Method):
        __path__ = ['printers', '$printerservername']
        def _call(self, dirlist = None, path = None, prefix = None, depth = None):
            res = []
            printerlistcmd = self._getpath(Grimoire.Types.TreeRoot).directory.get.sysinfo(['local', 'printers', 'listprinters'], 'lpstat -a')
            queuelistcmd = self._getpath(Grimoire.Types.TreeRoot).directory.get.sysinfo(['local', 'printers', 'listqueue'], 'lpstat -o')

            # Get list of all printers
            if (dirlist):
                res = []
                found = 0
                printerpipe = os.popen(printerlistcmd)
                for printer in printerpipe.xreadlines():
                    printername = string.split(printer)[0]
                    printername = string.replace(printername, "_", " ")
                    res = res + [ (1, [ printername ])]
                    if (path == printername):
                        found = 1
                if len(path) == 1:
                    if found:
                        return [ 1, []]
                    else:
                        return []
                else:
                    return res
            else:
                # Make a status listing of all printer queues.
                printerpipe = os.popen(printerlistcmd)
                line = printerpipe.readline()
                while line != '':
                    if string.split(line)[0] != 'printer':
                        # A trailing line from an earlier printer - just print it!
                        res = res + [ line ]
                    else:
                        # This is a new printer.
                        printer = line
                        res = res + [ printer ]
                        if (string.split(printer)[-1] == "-"):
                            # Read the next line also
                            res = res + [ printerpipe.readline() ]
                        printername = string.split(printer)[1]
                        res = res + [ "Queue:\n" ]
                        qpipe = os.popen(queuelistcmd + " " + printername)
                        for qentry in qpipe.xreadlines():
                            res = res + [ qentry ]
                    res = res + [ "\n" ]
                    line = printerpipe.readline()
            
                return Grimoire.Types.AnnotatedValue(
                    None,
                    Grimoire.Types.Lines(*res))
            
        def _params(self):
            return Grimoire.Types.ParamsType.derive([], 0)
                
