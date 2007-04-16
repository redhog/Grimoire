#! /bin/sh

. Tools/getversion.sh

tla logs -f -s -D -c -r |
 while read version; read info; read summary; do
  date=$(date -d "$(echo "$info" | sed -e "s+      .*$++g")" +"%a, %d %b %Y %k:%M:%S %z")
  creator="$(echo "$info" | sed -e "s+^.*      ++g")"
  echo "grimoire ($(tlaversion2pkg "$version")) unstable; urgency=low";
  echo
  echo "  * $summary"
  echo
  echo " -- $creator  $date"
  echo
 done
