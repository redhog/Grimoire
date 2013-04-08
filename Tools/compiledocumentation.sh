#! /bin/sh

. Tools/getversion.sh
grimoire_vendor > Documentation/vendor
grimoire_version > Documentation/version

find Documentation -name *.docbook |
 while read name; do
  htmlname="$(echo "$name" | sed -e "s+\.docbook$+.html+")"
  echo "$name -> $htmlname"
  xsltproc \
   -o "$htmlname" \
   Tools/Styles/docbookhtml.xsl \
   "$name"
 done

