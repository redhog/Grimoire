#! /bin/sh

echo "Creating translation directories"
{
 tla inventory -s -d
 echo "."
} |
 grep -v "_Translations" |
 while read dir; do
  if [ ! -d "$dir/_Translations" ]; then
   echo "  $dir/_Translations"
   mkdir "$dir/_Translations"
  fi
 done

echo "Updating all .pot-files from python source files"
tla inventory -s -f |
 grep -e "\.py$" |
 while read path; do
  potpath="$(echo "$path" |
   sed \
    -e "s+^\(.*\)/\([^/]*\)\.py$+\1/_Translations/\2.pot+g" \
    -e "s+^\([^/]*\)\.py$+_Translations/\1.pot+g")"
  if [ $potpath -ot "$path" ]; then
   echo "  $path -> $potpath"
   Tools/pygettext -a -o "$potpath" "$path"
  fi
 done

echo "Updating all .pot-files for directories from pot-files in them"
tla inventory -s -d | grep -v "_Translations" | sort -r |
 while read dir; do
  potpath="$(echo "$dir" |
   sed \
    -e "s+^\(.*\)/\([^/]*\)$+\1/_Translations/\2.pot+g" \
    -e "s+^\([^/]*\)$+_Translations/\1.pot+g")"
  echo "  $dir -> $potpath"
  if [ -e "$potpath" ]; then
   find "$dir/_Translations/" -maxdepth 1 -name "*.pot" \( \! -name "_*" -o -name "__init__.pot" \) -newer "$potpath"
  else
   touch "$potpath"
   find "$dir/_Translations/" -maxdepth 1 -name "*.pot" \( \! -name "_*" -o -name "__init__.pot" \)
  fi |
   while read subpotpath; do
    echo "    $subpotpath -> $potpath"
    cat > "$subpotpath.name" <<EOF
# SOME DESCRIPTIVE TITLE.
# Copyright (C) YEAR ORGANIZATION
# FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.
#
msgid ""
msgstr ""
"Project-Id-Version: PACKAGE VERSION\n"
"POT-Creation-Date: Fri Jan  9 01:45:40 2004\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\n"
"Language-Team: LANGUAGE <LL@li.org>\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=iso-8859-1\n"
"Content-Transfer-Encoding: ENCODING\n"
"Generated-By: pygettext.py 1.4\n"

msgid "$(echo "$subpotpath" | sed -e "s+^.*/\([^/]*\)\.pot$+\1+g")"
msgstr ""
EOF
    msgcat --force-po --strict --use-first -o "$potpath.new" "$potpath" "$subpotpath" "$subpotpath.name"
    rm "$subpotpath.name"
    mv "$potpath.new" "$potpath"
   done
 done

echo "Updating .po-files from .pot-files"
tla inventory -s -d | grep -v "_Translations" |
 while read dir; do
  find "$dir/_Translations/" -maxdepth 1 -name "*.pot" |
   while read potfile; do
    echo "  $potfile"
    domain="$(echo "$potfile" | sed -e "s+^.*/\([^/]*\)\.pot$+\1+g")"
    find "$dir/_Translations/" -name "$domain.po" \! -newer "$potfile" |
     while read pofile; do
      echo "    $pofile <- $potfile"
      msgmerge -U "$pofile" "$potfile"
     done
   done
 done
