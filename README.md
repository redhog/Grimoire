Grimoire is an "action-tree", a tree-structured database (like LDAP) that stores system-administrative functions instaed of data, giving users access to different subsets of those functions and thus enabling them to manipulate the stored data, configuration and resources of a system. 

To administer a system using Grimoire, one must install a Grimoire-server on each computer whose resources one wants to manage and install/write modules that exports a tree of functions that manipulates those resources, e.g. functions to start/stop/restart the printer queue on the printer server or functions to add or remove users in LDAP. In addition one must install a central Grimoire-server that collects and merges those subtrees into one big tree of functions and makes that tree accessible to the users through a web(or other)-GUI, where a user can log in and point-and-click his/her way to the functions he/she is allowed to perform. 

TakeIT uses Grimoire to delegate authorization to perform certain system administration to any user in the system. For example to authorize a secretary to add new users and change passwords of users who have forgotten theirs, or to authorize the computer teacher to change the passwords of his/her students for the same reason, or to authorize and enable the local PC-technician, who does not know Linux, to restart printer-queues and install new printers. This frees TakeIT from the burden of such rutine tasks, and gives the user more control over their system, making everyone a winner. 

The flexible structure of Grimoire makes it easy to replicate functionality of existing advanced administration-systems (such as Novell NDS). Functions for basic system administrations are ready and we are currently using Grimoire in production to create user and machine accounts aswell as for printer queue management. 

Grimoire also has SQL connectivity. To manipulate an SQL-database from within Grimoire is thus as easy as manipulating an LDAP-tree or the local filesystem. 

The technologies behind Grimoire are Python (the modules must thus be written in Python) and SSL and for the web-GUI Apache, WebWare and FunFormKit are used. The SQL-connectivity is implemented for PostgreSQL at the moment, but other SQL-databases with python connectivity are also possible to support in the future. 

Grimoire is versioned using the GNU Arch SCM. To register the Grimoire archive and check out Grimoire, issue the command 
`tla register-archive "main AT grimoire.gna.org" "sftp COLON SLASH SLASH yourusername AT arch.gna.org/upload/grimoire/main.grimoire.gna.org"' 
