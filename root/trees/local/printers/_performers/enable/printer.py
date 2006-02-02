####################################################
# Grimoire method printers.manage.start()          #
# Restarts a printer in the CUPS                   #
# Written 2004-02-09 by Martin Bjornsson           #
####################################################

import Grimoire.Utils, Grimoire.Performer, Grimoire.Types, types, os, string

class Performer(Grimoire.Performer.Base):
    class printer(Grimoire.Performer.SubMethod):
        __path__ = ['printer', '$printerservername']        
        def _call(self, path):
            if (len(path) != 1):
                raise Exception(
                    Grimoire.Types.Formattable(
                    "Error starting printer: No printer specified."))
            else:
                # Find the path of the most commonly used cups enable
                # command (used in Fedora Core 2, anyway)
                
                enablepath = string.split(os.popen('which enable').readline())[0]
                print enablepath
                enablecmd = self._getpath(Grimoire.Types.TreeRoot).directory.get.sysinfo(['local', 'printers', 'enable'], enablepath)

                printer = path[0]
                printer = string.replace(printer, " ", "_")                
                exitcode = os.system(enablecmd + " " + printer + " > /dev/null")
                if exitcode == 0:
                    return Grimoire.Types.AnnotatedValue(
                        None,
                        Grimoire.Types.Formattable(
                        "Started printer %(printername)s", printername=printer))
                else:
                    raise Exception(
                        Grimoire.Types.Formattable(
                        "Error starting printer %(printername)s",
                        printername=printer))

        def _dir(self, path, depth):
            # Get list of all printers
            return self._getpath(Grimoire.Types.MethodBase, 1,
                                 ['list', 'printers', '$printerservername']
                                 )(1, path, [], depth)

        def _params(self, path):
            return Grimoire.Types.AnnotatedValue(
                Grimoire.Types.ParamsType.derive([], 0),
                Grimoire.Types.Formattable(
                "Starting the printer queue to the printer %(printername)s",
                printername=path[0]))
