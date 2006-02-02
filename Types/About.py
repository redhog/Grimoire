import Composable

class CopyrightChange(Composable.Mapping):
    def __init__(self, type, year, name, email):
        Composable.Mapping.__init__(
            self,
            type=type,
            year=year,
            name=name,
            email=email)

class Copyright(CopyrightChange):
    def __init__(self, *arg, **kw):
        CopyrightChange.__init__(self, u'Copyright', *arg, **kw)

class Change(CopyrightChange):
    def __init__(self, *arg, **kw):
        CopyrightChange.__init__(self, u'Change', *arg, **kw)

class AboutItem(Composable.Mapping):
    def __init__(self, name, versionname, copyright, changes, licenseURL, licenseText):
        Composable.Mapping.__init__(
            self,
            name=name,
            versionname=versionname,
            copyright=copyright,
            changes=changes,
            licenseURL=licenseURL,
            licenseText=licenseText)
