#! /bin/bash

umask 077

clear
cat <<EOF
Welcome to the Grimoire LDAP server configuration and setup wizard!
This wizard will create a new LDAP server configuration and LDAP
database entries required for Grimoire. To do so, it needs some
information from you, which you will have to enter.

There is no way to go back to a previous question, so always take a
second look at your input before hitting [enter], or you will have to
do it all over from the start again to get it right.

Some questions will have default values, which are shown within
brackets []. Just hitting [enter] will give you the default value.

Some questions only allow an answer out of some specified set of
values. The allowed values will be shown or described within
parenthesis ().

NOTE: Under no circumstances will this script modify your system
without asking for your permission to do so. At the end, you will be
given an option to either let the script do the
installation/configuration, or just have it write the
configuration-files to the current directory for you to install by
hand.

================================================================================
EOF

source functions.sh

#### Load any saved values

if [ -e "$savefile" ]; then
 echo "Loading saved values..."
 source "$savefile"
fi


#### Server layout
export skeleton_roles="ldap cyrus_mail grimoire_ldap grimoire_home grimoire_group_home grimoire_courier_mail grimoire_cyrus_mail grimoire_grimweb grimoire_printers"
export skeleton_ldap_description="OpenLDAP database server"
export skeleton_cyrus_mail_description="Cyrus IMAPd mail server"
export skeleton_grimoire_ldap_description="Grimoire LDAP tree server (Main Grimoire tree server)"
export skeleton_grimoire_home_description="Grimoire Filesystem tree server for home directories"
export skeleton_grimoire_group_home_description="Grimoire Filesystem tree server for group home directories"
export skeleton_grimoire_courier_mail_description="Grimoire Filesystem tree server integration with the Curier IMAP server"
export skeleton_grimoire_cyrus_mail_description="Grimoire Cyrus tree server for integration with the Cyrus IMAPd server"
export skeleton_grimoire_grimweb_description="Web UI server (Webware server)"
export skeleton_grimoire_printers_description="CUPS printer server and Grimoire print controller server"

cat <<EOF

Grimoire services can be spread out over a network of serveral
machines. Each of these machines needs to be configured properly (and
differently) for the system to work correctly. This script will
generate configuration files for all machines in your system, and
optionally configure all services that will be running on this local
machine. To do so, it will need to know your network/server layout,
that is, which machine will be running each of these services:

EOF

for role in $skeleton_roles; do
 echo "$(ref skeleton_${role}_description)"
done

cat <<EOF

NOTE: All these services _can_ be run on the same machine. You can
only use one alias for each physical machine.

EOF

previous="$(hostname -f)"
for role in $skeleton_roles; do
 readWithDefault skeleton_${role}_servername "$(ref skeleton_${role}_description)" "$previous"
 previous="$(ref skeleton_${role}_servername)"
 host="$(ref skeleton_${role}_servername)"
 export skeleton_${role}_server_varname="$(hostname2varname "$host")"
 [ "$(ref skeleton_$(ref skeleton_${role}_server_varname)_password)" ] || export skeleton_$(ref skeleton_${role}_server_varname)_password="$(genPassword 32)"
 export skeleton_${role}_serverid="$(ref skeleton_${role}_servername | tr . "\n" | tac | tr "\n" . | sed -e "s+\.$++g")"
 export skeleton_${role}_serverid_python="'$(ref skeleton_${role}_serverid | sed -e "s+\.+', '+g")'"
 export skeleton_$(ref skeleton_${role}_server_varname)_roles="$({ ref skeleton_$(ref skeleton_${role}_server_varname)_roles | tr " " "\n"; echo "$role"; } | sort | uniq | tr "\n" " ")"
done


#### LDAP realm
cat <<EOF

The LDAP realm is the base DN for the LDAP database. Normally, the
realm represent your internet DNS domain-name, and for Grimoire, this
is required. Thus, if your DNS domain-name is
mydepartement.mycompany.com, your LDAP realm will be
dc=mydepartement,dc=mycompany,dc=com.

EOF
readWithDefault skeleton_ldap_realm_dnsname "Internet DNS domain name for site" "$(echo "$skeleton_ldap_servername" | cut -d . -f 2-)"

export skeleton_ldap_realm="$(echo "$skeleton_ldap_realm_dnsname" | sed -e "s+^+dc=+g" -e "s+\.+,dc=+g")"
export skeleton_ldap_realm_naming="$(echo "$skeleton_ldap_realm_dnsname" | cut -d . -f 1)"


#### Samba domain
cat <<EOF

Samba/Windows uses a Windows Domain name to identify a cluster of
Samba/Windows servers and clients using the same authentication
database. This name is usually an UPPERCSESHRTNME version of the
DNS domain name of the company or departement, or just the first
component of the DNS domain name.

EOF
readWithDefault skeleton_samba_domain "Samba domain name" "$skeleton_ldap_realm_naming"


#### Admin passwords
cat <<EOF
The LDAP administrative account cn=admin,$skeleton_ldap_realm is used
internally by Grimoire for its operations on the database. This
account can also be used manually to connect to the LDAP server and
perform various administrative tasks such as backup of its
entries. The password for this account must be filled in in the
Grimoire config-file (/etc/Grimoire/Config.py) for the Grimoire LDAP
support to work.

The account
uid=superadmin,ou=Administrators,ou=People,$skeleton_ldap_realm is a
Grimoire administrative account with full privilegies.

As most administrative tasks to be carried out using Grimoire does not
need full privilegies, another account,
uid=demoadmin,ou=Administrators,ou=People,$skeleton_ldap_realm will be
created.

You can create new accounts with varying privilegies, as well as
delete any of these accounts, later on from within Grimoire.

EOF

readPassword skeleton_$(ref skeleton_ldap_server_varname)_password "Password for cn=admin,$skeleton_ldap_realm" "$(genPassword 8)"
readPassword skeleton_superadmin_password "Password for uid=superadmin,ou=Administrators,ou=People,$skeleton_ldap_realm" "$(genPassword 8)"
readPassword skeleton_demoadmin_password "Password for uid=demoadmin,ou=Administrators,ou=People,$skeleton_ldap_realm" "$(genPassword 8)"

export skeleton_rootpassword="rootpw \"$(ref skeleton_${skeleton_ldap_server_varname}_password)\""


#### Language
cat <<EOF

You must select a locale (language) for the two administrative
accounts. To get a list of available locales on your system, you may
use the 'locale -a' command in another terminal.

NOTE: You should be using UTF-8 on your system, as that is the only
character encoding system supported by Grimoire. So be sure to select
a locale using UTF-8 character encoding.

EOF

readWithDefault skeleton_language "Language for administrator accounts" "$LANG"


#### Maildomains
cat <<EOF

When Grimoire creates a new user it will always create an
email-adress with the same username as the one used by the user to log
in to the system, and optionally another with some other username.

These two adresses can use different domain-names, the mail domainname
and the secondary mail domainname (for the optional adress).

That is, the adresses created will be username@mailDomain and
mailusername@secondaryMailDomain respectively.

The values filled in here are the defaults for the system, and can be
overridden with other values for different groups of users.

EOF

readWithDefault skeleton_mail_domain "Default mail domain" "$skeleton_ldap_realm_dnsname"
readWithDefault skeleton_mail_second_domain "Default secondary mail domain" "$skeleton_ldap_realm_dnsname"


#### Directory paths
cat <<EOF

When Grimoire creates a new user it will create a home directory and a
mail directory for the user.

To do so, it needs to know where the directory with home directories
is mounted in the filesystem on client machines, such as
/mnt/net/home/people or /home, and where it is mounted in the
filesystem on the home server machine, such as
/mnt/bigdisk5/home/people, and likeweise for the directory with group
home directories and for the directory of mail directories.

EOF

readWithDefault skeleton_homedir_server_path_unix "Server mount point for the directory of home directories" "/home/people"
readWithDefault skeleton_homedir_client_path_unix "Client mount point for the directory of home directories" "$skeleton_homedir_server_path_unix"
export skeleton_homedir_path="$skeleton_grimoire_home_serverid$(echo "$skeleton_homedir_client_path_unix" | tr / .)"
export skeleton_homedir_client_path="$(echo "$skeleton_homedir_client_path_unix" | sed -e "s+^/++g" | tr / .)"

readWithDefault skeleton_group_homedir_server_path_unix "Server mount point for the directory of group home directories" "/home/groups"
readWithDefault skeleton_group_homedir_client_path_unix "Client mount point for the directory of group home directories" "$skeleton_group_homedir_server_path_unix"
export skeleton_group_homedir_path="$skeleton_grimoire_group_home_serverid$(echo "$skeleton_group_homedir_client_path_unix" | tr / .)"
export skeleton_group_homedir_client_path="$(echo "$skeleton_group_homedir_client_path_unix" | sed -e "s+^/++g" | tr / .)"

readWithDefault skeleton_maildir_server_path_unix "Server mount point for the directory of mail directories" "/mail"
readWithDefault skeleton_maildir_client_path_unix "Client mount point for the directory of mail directories" "$skeleton_maildir_server_path_unix"
export skeleton_maildir_path="$skeleton_grimoire_cyrus_mail_serverid$(echo "$skeleton_maildir_client_path_unix" | tr / .)"
export skeleton_maildir_client_path="$(echo "$skeleton_maildir_client_path_unix" | sed -e "s+^/++g" | tr / .)"


#### Server commands
cat <<EOF

This script needs to know how to start and stop the OpenLDAP and the
Grimoire server processes, and where various files should reside. If
you are using Fedora or any other system with a System V init, the
default values will probably be correct, at least for the commands...

EOF

if [ -e "/etc/init.d/ldap" ]; then
 skeleton_ldap_start_default="/etc/init.d/ldap start"
 skeleton_ldap_stop_default="/etc/init.d/ldap stop"
elif [ -e "/etc/init.d/slapd" ]; then
 skeleton_ldap_start_default="/etc/init.d/slapd start"
 skeleton_ldap_stop_default="/etc/init.d/slapd stop"
fi
readWithDefault skeleton_ldap_start "Command to start the LDAP server" "$skeleton_ldap_start_default"
readWithDefault skeleton_ldap_stop "Command to stop the LDAP server" "$skeleton_ldap_stop_default"

[ -e "/etc/openldap" ] && skeleton_ldap_configdir_default="/etc/openldap"
[ -e "/etc/ldap" ] && skeleton_ldap_configdir_default="/etc/ldap"
readWithDefault skeleton_ldap_configdir "LDAP server configuration directory" "$skeleton_ldap_configdir_default"
[ -e "/var/lib/ldap" ] && skeleton_ldap_dbdir_default="/var/lib/ldap"
readWithDefault skeleton_ldap_dbdir "LDAP database directory" "$skeleton_ldap_dbdir_default"

if [ -e "/etc/init.d/grimoire" ]; then
 skeleton_grimoire_start_default="/etc/init.d/grimoire start"
 skeleton_grimoire_stop_default="/etc/init.d/grimoire stop"
fi
readWithDefault skeleton_grimoire_start "Command to start the Grimoire server" "$skeleton_grimoire_start_default" 
readWithDefault skeleton_grimoire_stop "Command to stop the Grimoire server" "$skeleton_grimoire_stop_default" 

[ -e "/etc/init.d/httpd" ] && skeleton_httpd_restart_default="/etc/init.d/httpd restart"
[ -e "/etc/init.d/apache2" ] && skeleton_httpd_restart_default="/etc/init.d/apache2 restart"
[ -e "/etc/init.d/apache" ] && skeleton_httpd_restart_default="/etc/init.d/apache restart"
readWithDefault skeleton_httpd_restart "Command to restart the web-server" "$skeleton_httpd_restart_default" 

[ -e "/etc/init.d/webkit" ] && skeleton_webkit_restart_default="/etc/init.d/webkit restart"
readWithDefault skeleton_webkit_restart "Command to restart the WebWare application-server" "$skeleton_webkit_restart_default" 


#### Generate Samba SID
cat <<EOF

All information needed for configuring the LDAP database has now been
gathered.

EOF

if ! [ "$skeleton_samba_sid" ]; then
 echo -n "Generating Samba domain identifier (SID)..."
 export skeleton_samba_sid=""
 for ((x=0;x<10;x++)); do skeleton_samba_sid=$skeleton_samba_sid$(echo $RANDOM | cut -c 1); done
 skeleton_samba_sid="$skeleton_samba_sid-"
 for ((x=0;x<10;x++)); do skeleton_samba_sid=$skeleton_samba_sid$(echo $RANDOM | cut -c 1); done
 skeleton_samba_sid="$skeleton_samba_sid-"
 for ((x=0;x<10;x++)); do skeleton_samba_sid=$skeleton_samba_sid$(echo $RANDOM | cut -c 1); done
 echo "done."
fi

#### Generate some composite values for the LDAP content

export skeleton_hosts="$(uniqMachines $skeleton_roles)"
export skeleton_grimoire_filesystem_hosts="$(uniqMachines grimoire_home grimoire_group_home grimoire_courier_mail)"
export skeleton_grimoire_cyrus_hosts="$skeleton_grimoire_cyrus_mail_servername"
export skeleton_grimoire_printers_hosts="$skeleton_grimoire_printers_servername"

export skeleton_grimoire_initcommands=""
for host in $skeleton_grimoire_filesystem_hosts; do
 skeleton_grimoire_initcommands="grimoireInitCommand: _.introspection.mount($(grimoireConnect "$skeleton_ldap_servername" "$host").trees.local.filesystem('filesystem', '$(ref skeleton_$(hostname2varname "$host")_password)'))
$skeleton_grimoire_initcommands"
done
for host in $skeleton_grimoire_cyrus_hosts; do
 skeleton_grimoire_initcommands="grimoireInitCommand: _.introspection.mount($(grimoireConnect "$skeleton_ldap_servername" "$host").trees.local.cyrus('cyrus', '$(ref skeleton_$(hostname2varname "$host")_password)'))
$skeleton_grimoire_initcommands"
done
for host in $skeleton_grimoire_printers_hosts; do
 skeleton_grimoire_initcommands="grimoireInitCommand: _.introspection.mount($(grimoireConnect "$skeleton_ldap_servername" "$host").trees.local.printers('printers', '$(ref skeleton_$(hostname2varname "$host")_password)'))
$skeleton_grimoire_initcommands"
done

export skeleton_grimoire_grimweb_tree="$(grimoireConnect "$skeleton_grimoire_grimweb_servername" "$skeleton_grimoire_ldap_servername").trees.local.ldap"

#### Generating files

echo "Generating a save-file of all user input..."
declare | grep -e "^skeleton" | sed -e "s+^+export +g" > "$savefile"

./genfiles.sh

echo "done."


#### Set up the system
if [ -d "$genfiles/$(hostname)" ]; then
 cd "$genfiles/$(hostname)"

 cat <<EOF

You can now either let this script set up the system using the
generated files, or do the rest by hand.

EOF

 find etc/ \! -type d |
  while read path; do
   if [ -e  "/$path" ]; then
    cat <<EOF
WARNING: If you let the script configure your system, your current
/$path
will be moved to
/$path.old.

EOF
   fi
  done

 readWithDefault proceed "Do you want to proceed with configuring the system (y/n)?" y
else
 proceed=n
fi

if [ "$proceed" == "n" ]; then
 ## Inform user what to do to install
 cat <<EOF

To install your system, for each machine, go to the directory
"$genfiles/\$HOSTNAME" and follow the instructions in the README- or
setup.sh-files found therein.
EOF
else
 ## Install
 ./setup.sh
 cat <<EOF

All roles local to this machine are now configured. To finnish
installing your system, for each non-localhost machine, go to the
directory "$genfiles/\$HOSTNAME" and follow the instructions in the
setup.sh-files found therein.
EOF
fi
