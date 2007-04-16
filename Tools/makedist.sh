#! /bin/sh

disttype=deb
server=download.gna.org:/upload/grimoire/

params=0
while (($# >> 0)); do
 case $1 in
  --disttype=*) disttype="$(echo "$1" | sed -e "s+^--disttype=++g")";;
  --upload) upload=y;;
  --server=*) server="$(echo "$1" | sed -e "s+^--server=++g")";;
  --*) help=1;;
 esac
 shift
done

if [ "$help" ]; then
 cat <<EOF
Usage: makedist.sh [--disttype=tgz|rpm|deb] [--upload [--server=UPLOAD_DIRECTORY]]

Generate and optionally upload a distribution.
Default disttype is deb.
Default UPLOAD_DIRECTORY is '$server'.
EOF
 exit 1
fi

. Tools/getversion.sh
VENDOR="$(grimoire_vendor)"
VERSION="$(grimoire_version)"

echo "Building $disttype for $VERSION from $VENDOR:"

echo "Removing old files..."
rm -rf "=dist/Grimoire-$VERSION"

echo "Copying files..."
{
 echo "."
 tla inventory -s -d
} |
 sed -e "s+(sp)+ +g" |
 while read dir; do
  mkdir -p "=dist/Grimoire-$VERSION/$dir"
  cp -a "$dir/.arch-ids" "=dist/Grimoire-$VERSION/$dir/.arch-ids"
 done

tla inventory -s -f |
 sed -e "s+(sp)+ +g" |
 while read file; do
  cp -d "$file" "=dist/Grimoire-$VERSION/$file"
 done

mkdir -p "=dist/Grimoire-$VERSION/{arch}"
ls "{arch}" |
 grep -v "++pristine-trees" |
 while read file; do
  cp -a -d "{arch}/$file" "=dist/Grimoire-$VERSION/{arch}/$file"
done

echo "Making spec-file..."
m4 \
 -DVENDOR="$VENDOR" \
 -DVERSION="$VERSION" \
 < "Tools/Grimoire.spec.in" > "=dist/Grimoire-$VERSION/Grimoire.spec"

cd "=dist"

echo "Making tar.gz..."
tar -czf "Grimoire-$VERSION.tgz" "Grimoire-$VERSION"

case "$disttype" in
 rpm)
  echo "Building rpm..."
  rpmbuild -ta "Grimoire-$VERSION.tgz";;
 deb)
  cd Grimoire-$VERSION
  Tools/log2aptlog.sh > debian/changelog
  dpkg-buildpackage
esac

if [ "$upload" ]; then
 echo "Uploading..."
 rsync -a "$server" "download/"
 case "$disttype" in
  rpm)
   bindst="$(rpm -E "%{_rpmdir}/%{_build_arch}")"
   srcdst="$(rpm -E "%{_srcrpmdir}")"
   cp "$bindst/Grimoire-$VERSION-1_ti_1.i386.rpm" "download/RPMS"
   cp "$bindst/Grimoire-"*"-$VERSION-1_ti_1.i386.rpm" "download/RPMS"
   cp "$srcdst/Grimoire-$VERSION-1_ti_1.src.rpm" "download/RPMS"
   yum-arch "download/RPMS"
   createrepo "download/RPMS"
   ;;
  tgz)
   cp "Grimoire-$VERSION.tgz" "download/Grimoire-$VERSION.tgz"
   ;;
 esac
 rsync -a "download/" "$server"
fi
