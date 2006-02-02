#! /bin/sh

tla inventory -s |
 grep "^.*\.po$" |
 while read pofile; do
  mofile="$(echo "$pofile" | sed -e "s+\.po$+.mo+g")"
  if [ ! -e "$mofile" -o "$mofile" -ot "$pofile" ]; then
   echo "$pofile -> $mofile"
   msgfmt -o "$mofile" "$pofile"
  fi
 done
