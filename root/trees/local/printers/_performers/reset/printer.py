####################################################
# Grimoire method printers.manage.reset()          #
# Cancels all jobs from a CUPS printing queue      #
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
                    "Error resetting printer queue: No printer specified."))
            else:
                resetcmd = self._getpath(Grimoire.Types.TreeRoot).directory.get.stsinfo(['local', 'printers', 'reset'], 'cancel -a')
                printer = path[0]
                printer = string.replace(printer, "-", "_")
                exitcode = os.system(resetcmd + " " + printer + " > /dev/null")
                if exitcode == 0:
                    return Grimoire.Types.AnnotatedValue(
                        None,
                        Grimoire.Types.Formattable(
                        "Reset printer queue to printer %(printername)s",
                        printername=printer))
                else:
                    raise Exception(
                        Grimoire.Types.Formattable(
                        "Error resetting printer queue to printer %(printername)s",
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
                "Cancel all jobs in the printer queue to the printer %(printername)s",
                printername=path[0]))

