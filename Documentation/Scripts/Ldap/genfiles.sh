#! /bin/bash

umask 077

source functions.sh
if ! [ -e "$savefile" ]; then
 echo "No savefile found. Please run setup.sh"
 exit 1
fi
source "$savefile"
export skeleton_homedir_server_path="$(echo "$skeleton_homedir_server_path_unix" | tr / .)"
export skeleton_homedir_client_path="$(echo "$skeleton_homedir_client_path_unix" | sed -e "s+^/++g" | tr / .)"
export skeleton_group_homedir_server_path="$(echo "$skeleton_group_homedir_server_path_unix" | tr / .)"
export skeleton_group_homedir_client_path="$(echo "$skeleton_group_homedir_client_path_unix" | sed -e "s+^/++g" | tr / .)"
export skeleton_maildir_server_path="$(echo "$skeleton_maildir_server_path_unix" | tr / .)"
export skeleton_maildir_client_path="$(echo "$skeleton_maildir_client_path_unix" | sed -e "s+^/++g" | tr / .)"

extensions="."
if [ -f /etc/debian_version ]; then
 extensions="$extensions .debian"
fi

echo -n "Removing old files..."
rm -rf "$genfiles"
echo "done."

echo -n "Generating files..."

# OpenLDAP database server machine
ldapgenfiles="$genfiles/$skeleton_ldap_servername"
mkdir -p "$ldapgenfiles"
writesecret ${skeleton_ldap_server_varname}_password "$ldapgenfiles/admin_password.secret"
writesecret superadmin_password "$ldapgenfiles/superadmin_password.secret"
writesecret demoadmin_password "$ldapgenfiles/demoadmin_password.secret"


for role
 in \
  cyrus_mail \
  grimoire_courier_mail \
  grimoire_cyrus_mail \
  grimoire_grimweb \
  grimoire_group_home \
  grimoire_home \
  grimoire_ldap \
  grimoire_printers \
  horde \
  mediawiki \
  ldap;
 do
  if [ "$(ref skeleton_${role}_servername)" ]; then
   export skeleton_role="$role"
   instantiateTemplates "templates/functions.in" "templates/$role" "$genfiles/$(ref skeleton_${role}_servername)" "$extensions"
  fi
 done

echo "done."
