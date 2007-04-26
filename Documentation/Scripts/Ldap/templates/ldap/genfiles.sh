#! /bin/sh

chown ldap:ldap "$ldapgenfiles/$skeleton_ldap_configdir/slapd.conf"
chmod ugo+r "$ldapgenfiles/$skeleton_ldap_configdir/ldap.conf"
