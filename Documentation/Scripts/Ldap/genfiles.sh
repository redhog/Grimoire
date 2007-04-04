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

# Filesystem machines
export skeleton_servertype=""
for skeleton_servertype in home group_home courier_mail; do
 if [ "$(ref skeleton_grimoire_${skeleton_servertype}_servername)" ]; then
  instantiateTemplates "templates/functions.in" "templates/filesystem" "$genfiles/$(ref skeleton_grimoire_${skeleton_servertype}_servername)"
 fi
done

# Cyrus machine
instantiateTemplates "templates/functions.in" "templates/cyrus_mail" "$genfiles/$(ref skeleton_cyrus_mail_servername)"

# Cyrus Grimoire Tree machine
instantiateTemplates "templates/functions.in" "templates/grimoire_cyrus_mail" "$genfiles/$(ref skeleton_grimoire_cyrus_mail_servername)"

# Grimweb machine
instantiateTemplates "templates/functions.in" "templates/grimoire_grimweb" "$genfiles/$skeleton_grimoire_grimweb_servername"

# CUPS server
printersgenfiles="$genfiles/$skeleton_grimoire_printers_servername"
mkdir -p "$printersgenfiles/$settings/local"
m4 templates/functions.in templates/printers.py.in > "$printersgenfiles/$settings/local/printers.py"

# Generate files for all machines
export skeleton_servername
for skeleton_servername in $skeleton_hosts; do
 export skeleton_server_varname="$(hostname2varname "$skeleton_servername")"
 hostgenfiles="$genfiles/$skeleton_servername"
 m4 templates/functions.in templates/setup.sh.in >> "$hostgenfiles/setup.sh"
 chmod u+x "$hostgenfiles/setup.sh"
 instantiateTemplates "templates/functions.in" "templates/all" "$hostgenfiles"
done

echo "done."
