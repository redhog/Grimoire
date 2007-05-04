#! /bin/bash

umask 077

source functions.sh
if ! [ -e "$savefile" ]; then
 echo "No savefile found. Please run setup.sh"
 exit 1
fi
source "$savefile"

extensions="."
if [ -f /etc/debian_version ]; then
 extensions="$extensions .debian"
fi

echo -n "Removing old files..."
rm -rf "$genfiles"
echo "done."

echo -n "Generating files..."

export skeleton_servertype
for skeleton_servername in $skeleton_hosts; do
 export skeleton_server_varname="$(hostname2varname "$skeleton_servername")"
 export skeleton_${skeleton_server_varname}_functions=""
 export skeleton_${skeleton_server_varname}_shutdown=""
 export skeleton_${skeleton_server_varname}_configure=""
 export skeleton_${skeleton_server_varname}_restart=""
done

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
   export skeleton_server_varname="$(hostname2varname "$(ref skeleton_${role}_servername)")"
   instantiateTemplates "templates/functions.in" "templates/$role" "$genfiles/$(ref skeleton_${role}_servername)" "$extensions"
  fi
 done

echo "done."
