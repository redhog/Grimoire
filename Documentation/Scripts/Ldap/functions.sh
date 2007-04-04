#/bin/bash

[ "$genfiles" ] || export genfiles="Generated_configuration_files"
[ "$savefile" ] || export savefile="setup.save"
export settings="etc/Grimoire/Config.d/parameters/_settings"

# Get the value of a variable named $1.
ref () { eval echo \$$1; }

# Read a value from the user into the variable named by $1 with prompt
# $2 and default value $3
readWithDefault () {
 varname="$1"
 prompt="$2"
 default="$(ref "$varname")"
 [ "$default" ] || default="$3"
 if [ "$default" ]; then
  echo -n "$prompt [$default]: "
 else
  echo -n "$prompt: "
 fi
 read $varname
 [ "$(ref "$varname")" ] || { [ "$default" ] && export "$varname"="$default"; }
 export  $varname
}

# Read a password from the user into the variable named by $1 with
# prompt $2
readPassword () {
 varname="$1"
 prompt="$2"
 default="$(ref "$varname")"
 [ "$default" ] || default="$3"
 [ "$default" ] || default="$(genPassword 8)"

 export ${varname}=x
 export ${varname}_repeat=y

 stty -echo
 while [ "$(ref "$varname")" != "$(ref "${varname}_repeat")" ]; do
  echo -n "$prompt [$default]: "
  read $varname

  if [ "$(ref "$varname")" ]; then
   echo

   echo -n "$prompt (repeat): "
   read ${varname}_repeat
   echo

   if [ "$(ref "$varname")" != "$(ref "${varname}_repeat")" ]; then
    echo "Passwords dows not match. Please try again."
   fi
  else
   echo "(default password '$default' choosen)"
   export ${varname}="$default"
   export ${varname}_repeat="$default"
  fi
 done
 stty echo
}

# Generate a random password of length $1
genPassword() {
 length="$1"
 matrix="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
 pass=""
 for ((n = 0; n < $length; n++)); do
  pass="$pass${matrix:$(($RANDOM%${#matrix})):1}"
 done
 echo -n $pass
}

# Write a password in ${skeleton_$1} to the file $2, without
# passing it as a command-line argument to any program.
writesecret () {
 tr -d "\n" > "$2" <<EOF
$(ref skeleton_$1)
EOF
}

# Gives the variable name representation of a hostname
hostname2varname () { echo "$1" | tr ".-" "__"; }

# Generate a list of unique hostnames for a set of roles $*
uniqMachines () {
 for role in "$@"; do
  echo "$(ref skeleton_${role}_servername)"
 done | sort | uniq
}

# Generates a Grimoire expression to connect to a machine $2 from
# another machine $1. If the two machines are the same, no network
# connection will be used.
grimoireConnect () {
 src="$1"
 dst="$2"

 if [ "$src" == "$dst" ]; then
  echo "_"
 else
  echo "_.trees.remote.dirt.$(echo "$dst" | sed -e "s+\\.+\\\\.+g")()"
 fi
}

instantiateTemplates () {
 functions="$1"
 templates="$2"
 destination="$3"

 find ${templates} -type d |
  while read name; do
   dst="${destination}/$(echo "${name}" | sed -e "s+^${templates}$++g" -e "s+^${templates}/\(.*\)$+\1+g")"
   mkdir -p "${dst}"
   chmod --reference="${name}" "${dst}"
  done
 find ${templates} \! -type d -a -name "*.in" |
  while read name; do
   dst="${destination}/$(echo "${name}" | sed -e "s+^${templates}/\(.*\)\.in$+\1+g")"
   m4 ${functions} "${name}" > "${dst}"
   chmod --reference="${name}" "${dst}"
  done
 find ${templates} \! -type d -a \! -name "*.in" |
  while read name; do
   dst="${destination}/$(echo "${name}" | sed -e "s+^${templates}/\(.*\)$+\1+g")"
   cp -p "${name}" "${dst}"
  done
}
