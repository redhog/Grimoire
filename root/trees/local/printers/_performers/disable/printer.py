####################################################
# Grimoire method printers.manage.stop()           #
# Stops a CUPS printer queue                       #
# Written 2004-02-10 by Martin Bjornsson           #
####################################################

import Grimoire.Utils, Grimoire.Performer, Grimoire.Types, types, os, string

class Performer(Grimoire.Performer.Base):
    class printer(Grimoire.Performer.SubMethod):
        __path__ = ['printer', '$printerservername']
        def _call(self, path):
            if (len(path) != 1):
                raise Exception(
                    Grimoire.Types.Formattable(
                    "Error stopping printer: No printer specified."))
            else:
                # Find the path of the most commonly used cups disable
                # command (used in Fedora Core 2, anyway)                
                disablepath = string.split(os.popen('which disable').readline())[0]
                disablecmd = self._getpath(Grimoire.Types.TreeRoot).directory.get.sysinfo(['local', 'printers', 'disable'], disablepath)

                printer = path[0]
                printer = string.replace(printer, "-", "_")
                exitcode = os.system(disablecmd + " " + printer + " > /dev/null")
                if exitcode == 0:
                    return Grimoire.Types.AnnotatedValue(
                        None,
                        Grimoire.Types.Formattable("Stopped printer %(printername)s", printername=printer))
                else:
                    raise Exception(
                        Grimoire.Types.Formattable(
                        "Error stopping printer %(printername)s",
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
                "Stopping the printer queue to the printer %(printername)s",
                printername=path[0]))
