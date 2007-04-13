#! /bin/bash

umask 077

source functions.sh
if ! [ -e "$savefile" ]; then
 echo "No savefile found. Please run setup.sh"
 exit 1
fi
source "$savefile"

if [ -f /etc/debian_version ]; then
 linux_dist_ext=.debian
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
mkdir -p "$ldapgenfiles/$skeleton_ldap_configdir"
m4 templates/functions.in templates/basecontent.ldif.in > "$ldapgenfiles/basecontent.ldif"
m4 templates/functions.in templates/slapd.conf.in${linux_dist_ext} > "$ldapgenfiles/$skeleton_ldap_configdir/slapd.conf"
chown ldap:ldap "$ldapgenfiles/$skeleton_ldap_configdir/slapd.conf"
m4 templates/functions.in templates/ldap.conf.in > "$ldapgenfiles/$skeleton_ldap_configdir/ldap.conf"
chmod ugo+r "$ldapgenfiles/$skeleton_ldap_configdir/ldap.conf"
writesecret ${skeleton_ldap_server_varname}_password "$ldapgenfiles/admin_password.secret"
writesecret superadmin_password "$ldapgenfiles/superadmin_password.secret"
writesecret demoadmin_password "$ldapgenfiles/demoadmin_password.secret"

# Grimoire LDAP tree server machine
grimldapgenfiles="$genfiles/$skeleton_grimoire_ldap_servername"
mkdir -p "$grimldapgenfiles/$skeleton_ldap_configdir"
mkdir -p "$grimldapgenfiles/$settings/local"
m4 templates/functions.in templates/ldap.conf.in > "$grimldapgenfiles/$skeleton_ldap_configdir/ldap.conf"
chmod ugo+r "$grimldapgenfiles/$skeleton_ldap_configdir/ldap.conf"
m4 templates/functions.in templates/ldap.py.in > "$grimldapgenfiles/$settings/local/ldap.py"

for role
 in \
  grimoire_home \
  grimoire_group_home \
  grimoire_courier_mail \
  cyrus_mail \
  grimoire_cyrus_mail \
  horde \
  grimoire_grimweb;
 do
  if [ "$(ref skeleton_${role}_servername)" ]; then
   instantiateTemplates "templates/functions.in" "templates/$role" "$genfiles/$(ref skeleton_${role}_servername)"
  fi
 done

# CUPS server
printersgenfiles="$genfiles/$skeleton_grimoire_printers_servername"
mkdir -p "$printersgenfiles/$settings/local"
m4 templates/functions.in templates/printers.py.in > "$printersgenfiles/$settings/local/printers.py"

# Generate files for all machines
export skeleton_servername
for skeleton_servername in $skeleton_hosts; do
 export skeleton_server_varname="$(hostname2varname "$skeleton_servername")"
 instantiateTemplates "templates/functions.in" "templates/all" "$genfiles/$skeleton_servername"
done

echo "done."
