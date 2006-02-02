import Grimoire.Types, os

grimoireAbout = "An Action tree implementation in Python"
grimoireCopyright = ('2003', 'TakeIT AB', 'redhog@takeit.se')
grimoireChanges = []
grimoireLicenseName = "GNU General Public License (GPL)"
grimoireLicenseURL = "http://www.fsf.org/licenses/gpl.html"
grimoireLicenseText = Grimoire.Types.Paragraphs(
    """This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or (at
your option) any later version.""",
    """This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.""",
    """You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
USA""",
    """In addition, as a special exception, AB TakeIT gives permission
to link the code of this program with the OpenSSL and the SSLeay
libraries (or with modified versions of them that uses the same
license), and distribute linked combinations including the these. You
must obey the GNU General Public License in all respects for all of
the code used other than OpenSSL/SSLeay. If you modify Grimoire, you
may extend this exception to your version, but you are not obligated
to do so. If you do not wish to do so, delete this exception statement
from your version.""")

_abouts = {}

def addAbout(aboutItem):
    name = Grimoire.Types.getValue(aboutItem['name'])
    versionname = Grimoire.Types.getValue(aboutItem['versionname'])
    if name not in _abouts:
        _abouts[name] = {}
    _abouts[name][versionname] = aboutItem

def abouts():
    res = []
    for name in _abouts.iterkeys():
        for versionname in _abouts[name].iterkeys():
            res += [_abouts[name][versionname]]
    return res


def getVersion():
    """Computes the current Grimoire version from the same source asn
    in the same manner as the Arch Revission Control System."""
    archDir = Grimoire.Types.LocalPath(__file__)[:-1] + ['{arch}']
    f = open(unicode(archDir + ['++default-version']))
    versionname = f.readline()[:-1] # Remove \n
    f.close()
    rep, localversion = versionname.split('/', 2)
    name, branch, version = localversion.split('--')
    patches = os.listdir(unicode(archDir + [name, name + '--' + branch, localversion, rep, 'patch-log']))
    patches = [int(patch.split('-')[-1]) for patch in patches]
    patches.sort()
    patchlevel = patches[-1]
    if patchlevel == 0:
        patchlevel = 'base-0'
    else:
        patchlevel = 'patch-' + unicode(patchlevel)
    versionname += '--' + patchlevel
    return versionname
grimoireVersion = getVersion()

addAbout(
    Grimoire.Types.AboutItem(
        Grimoire.Types.AnnotatedValue('Grimoire', grimoireAbout),
        grimoireVersion,
        Grimoire.Types.Copyright(*grimoireCopyright),
        [Grimoire.Types.Change(*x) for x in grimoireChanges],
        Grimoire.Types.TitledURILink(grimoireLicenseURL,
                                     grimoireLicenseName),
        grimoireLicenseText))
