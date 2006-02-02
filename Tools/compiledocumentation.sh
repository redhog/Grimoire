#! /bin/sh

. Tools/getversion.sh
grimoire_vendor > Documentation/vendor
grimoire_version > Documentation/version

xsltproc \
 -o Documentation/Overview.html \
 Tools/Styles/docbookhtml.xsl \
 Documentation/Overview.docbook
