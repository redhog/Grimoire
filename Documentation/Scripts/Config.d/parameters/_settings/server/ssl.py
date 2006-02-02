## SSL ##

# CA certificate to check the remote server against when connecting
set(['cacert'], '/etc/Grimoire/cacert.pem')

# server certificate to present to connecting clients
set(['cert'], '/etc/Grimoire/servercert.pem')

# Private key of server certificate
set(['privkey'], '/etc/Grimoire/serverprivkey.pem')
