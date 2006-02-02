/* databasschema för lansmusiken */;

drop table hours;
drop table productioninprojects;
drop table projects;
drop table shows;
drop table productions;
drop table producers;
drop table customers;
drop table users cascade;
drop table organizations;
drop table cooptypes;
drop table employmentforms;
drop table agegroups;
drop table showstates;
drop table showtypes;
drop table municipalities;
drop table regions;
drop table genres;
drop table projecttypes;
drop table organizationtypes;
drop table usergroups cascade;
drop table lansmusikeninfo;
drop table metainfo;
drop table groupabilities;
drop table userabilities;

create table metainfo(
"table" text,
"column" text,
"type" text,
"references" text,
"description" text
);

insert into metainfo values ('metainfo', 'table', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:unicode\', >', null, 'Table');
insert into metainfo values ('metainfo', 'column', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:unicode\', >', null, 'Column');
insert into metainfo values ('metainfo', 'type', '<\'Type\', \'__builtin__:object __builtin__:type\', >', 'Type');
insert into metainfo values ('metainfo', 'description', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:unicode\', >', null, 'Description');

create table lansmusikeninfo(
billingtime int,
account text,
address text,
zipcode text,
postaddress text,
email text,
telephone text,
mobile text,
fax text
);
insert into metainfo values ('lansmusikeninfo', null, null, null, 'Lansmusiken');
insert into metainfo values ('lansmusikeninfo', 'billingtime', '<\'Type\', \'__builtin__:object __builtin__:int\', >', null, 'Billing time');

insert into metainfo values ('lansmusikeninfo', 'account', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:str\', >', null, 'Account');
insert into metainfo values ('lansmusikeninfo', 'address', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:unicode\', >', null, 'Address');
insert into metainfo values ('lansmusikeninfo', 'zipcode', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:str\', >', null, 'ZIP-code');
insert into metainfo values ('lansmusikeninfo', 'postaddress', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:unicode\', >', null, 'Postal adress');
insert into metainfo values ('lansmusikeninfo', 'email', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:str\', >', null, 'E-mail');
insert into metainfo values ('lansmusikeninfo', 'telephone', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:str\', >', null, 'Telephone');
insert into metainfo values ('lansmusikeninfo', 'mobile', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:str\', >', null, 'Mobile phone');
insert into metainfo values ('lansmusikeninfo', 'fax', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:str\', >', null, 'Fax');

/* användargrupper för administration */
create table usergroups(
id serial primary key,
name text
);
insert into metainfo values ('usergroups', null, null, null, '%(name)s');
insert into metainfo values ('usergroups', 'id', '<\'Class\', \'Grimoire.Utils:GenericWrapper Grimoire.Utils:Wrapper Grimoire.Types.Derived:SerialType\', >', null, 'Id');
insert into metainfo values ('usergroups', 'name', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:unicode\', >', null, 'Name');

create table groupabilities(
usergroup integer references usergroups,
ability text
);

insert into metainfo values ('groupablities', 'group', '', 'usergroups', 'Group');
insert into metainfo values ('groupablities', 'ability', '', null, 'Ability');

/* statistikkategorier */
create table organizationtypes(
id serial primary key,
name text
);
insert into metainfo values ('organizationtypes', null, null, null, '%(name)s');
insert into metainfo values ('organizationtypes', 'id', '<\'Class\', \'Grimoire.Utils:GenericWrapper Grimoire.Utils:Wrapper Grimoire.Types.Derived:SerialType\', >', null, 'Id');
insert into metainfo values ('organizationtypes', 'name', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:unicode\', >', null, 'Name');

create table projecttypes(
id serial primary key,
name text
);
insert into metainfo values ('projecttypes', null, null, null, '%(name)s');
insert into metainfo values ('projecttypes', 'id', '<\'Class\', \'Grimoire.Utils:GenericWrapper Grimoire.Utils:Wrapper Grimoire.Types.Derived:SerialType\', >', null, 'Id');
insert into metainfo values ('projecttypes', 'name', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:unicode\', >', null, 'Name');

create table genres(
id serial primary key,
name text
);
insert into metainfo values ('genres', null, null, null, '%(name)s');
insert into metainfo values ('genres', 'id', '<\'Class\', \'Grimoire.Utils:GenericWrapper Grimoire.Utils:Wrapper Grimoire.Types.Derived:SerialType\', >', null, 'Id');
insert into metainfo values ('genres', 'name', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:unicode\', >', null, 'Name');

create table regions(
id serial primary key,
name text
);
insert into metainfo values ('regions', null, null, null, '%(name)s');
insert into metainfo values ('regions', 'id', '<\'Class\', \'Grimoire.Utils:GenericWrapper Grimoire.Utils:Wrapper Grimoire.Types.Derived:SerialType\', >', null, 'Id');
insert into metainfo values ('regions', 'name', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:unicode\', >', null, 'Name');

create table municipalities(
id serial primary key,
region integer references regions, 
name text
);
insert into metainfo values ('municipalities', null, null, null, '%(name)s in %(region.name)s');
insert into metainfo values ('municipalities', 'id', '<\'Class\', \'Grimoire.Utils:GenericWrapper Grimoire.Utils:Wrapper Grimoire.Types.Derived:SerialType\', >', null, 'Id');
insert into metainfo values ('municipalities', 'region', '<\'GenericReferenceType\', \'regions\')>', 'regions', 'Region');
insert into metainfo values ('municipalities', 'name', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:unicode\', >', null, 'Name');

create table showtypes(
id serial primary key,
description text
);
insert into metainfo values ('showtypes', null, null, null, '%(description)s');
insert into metainfo values ('showtypes', 'id', '<\'Class\', \'Grimoire.Utils:GenericWrapper Grimoire.Utils:Wrapper Grimoire.Types.Derived:SerialType\', >', null, 'Id');
insert into metainfo values ('showtypes', 'description', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:unicode\', >', null, 'Description');

create table showstates(
id serial primary key,
description text
);
insert into metainfo values ('showstates', null, null, null, '%(description)s');
insert into metainfo values ('showstates', 'id', '<\'Class\', \'Grimoire.Utils:GenericWrapper Grimoire.Utils:Wrapper Grimoire.Types.Derived:SerialType\', >', null, 'Id');
insert into metainfo values ('showstates', 'description', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:unicode\', >', null, 'Description');

create table agegroups(
id serial primary key,
description text,
lowerbound integer,
upperbound integer
);
insert into metainfo values ('agegroups', null, null, null, '%(description)s: %(lowerbound)s - %(upperbound)s');
insert into metainfo values ('agegroups', 'id', '<\'Class\', \'Grimoire.Utils:GenericWrapper Grimoire.Utils:Wrapper Grimoire.Types.Derived:SerialType\', >', null, 'Id');
insert into metainfo values ('agegroups', 'description', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:unicode\', >', null, 'Description');
insert into metainfo values ('agegroups', 'lowerbound', '<\'Type\', \'__builtin__:object __builtin__:int\', >', null, 'From age');
insert into metainfo values ('agegroups', 'upperbound', '<\'Type\', \'__builtin__:object __builtin__:int\', >', null, 'To age');

create table employmentforms(
id serial primary key,
description text
);
insert into metainfo values ('employmentforms', null, null, null, '%(description)s');
insert into metainfo values ('employmentforms', 'id', '<\'Class\', \'Grimoire.Utils:GenericWrapper Grimoire.Utils:Wrapper Grimoire.Types.Derived:SerialType\', >', null, 'Id');
insert into metainfo values ('employmentforms', 'description', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:unicode\', >', null, 'Description');

create table cooptypes(
id serial primary key,
description text
);
insert into metainfo values ('cooptypes', null, null, null, '%(description)s');
insert into metainfo values ('cooptypes', 'id', '<\'Class\', \'Grimoire.Utils:GenericWrapper Grimoire.Utils:Wrapper Grimoire.Types.Derived:SerialType\', >', null, 'Id');
insert into metainfo values ('cooptypes', 'description', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:unicode\', >', null, 'Description');

create table organizations(
id serial primary key,
name text, 
organizationtype integer references organizationtypes,
address text, 
zipcode text, 
postaddress text,
email text,
telephone text,
mobile text,
fax text
);
insert into metainfo values ('organization', null, null, null, '%(name)s (%(organizationtype)s)');
insert into metainfo values ('organization', 'id', '<\'Class\', \'Grimoire.Utils:GenericWrapper Grimoire.Utils:Wrapper Grimoire.Types.Derived:SerialType\', >', null, 'Id');
insert into metainfo values ('organization', 'name', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:unicode\', >', null, 'Name');
insert into metainfo values ('organization', 'organizationtype', '<\'GenericReferenceType\', \'organizationtypes\')>', 'organizationtypes', 'Type of organization');
insert into metainfo values ('organization', 'address', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:unicode\', >', null, 'Address');
insert into metainfo values ('organization', 'zipcode', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:str\', >', null, 'ZIP-code');
insert into metainfo values ('organization', 'postaddress', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:unicode\', >', null, 'Postal adress');
insert into metainfo values ('organization', 'email', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:str\', >', null, 'E-mail');
insert into metainfo values ('organization', 'telephone', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:str\', >', null, 'Telephone');
insert into metainfo values ('organization', 'mobile', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:str\', >', null, 'Mobile phone');
insert into metainfo values ('organization', 'fax', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:str\', >', null, 'Fax');

create table users(
id serial primary key,
usergroup integer references usergroups, 
givenname text, 
surname text, 
username text, 
password text, 
address text, 
zipcode text,
postaddress text, 
email text, 
telephone text,
mobile text,
fax text
);
insert into metainfo values ('users', null, null, null, '%(username)s (%(givenname)s %(surname)s) in %(usergroup.name)s');
insert into metainfo values ('users', 'id', '<\'Class\', \'Grimoire.Utils:GenericWrapper Grimoire.Utils:Wrapper Grimoire.Types.Derived:SerialType\', >', null, 'Id');
insert into metainfo values ('users', 'usergroup', '<\'GenericReferenceType\', \'usergroups\')>', 'usergroups', 'Group (type of user)');
insert into metainfo values ('users', 'givenname', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:unicode\', >', null, 'Given name');
insert into metainfo values ('users', 'surname', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:unicode\', >', null, 'Surname');
insert into metainfo values ('users', 'username', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:str\', >', null, 'Username');
insert into metainfo values ('users', 'password', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:str\', >', null, 'Password');
insert into metainfo values ('users', 'address', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:unicode\', >', null, 'Address');
insert into metainfo values ('users', 'zipcode', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:str\', >', null, 'ZIP-code');
insert into metainfo values ('users', 'postaddress', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:unicode\', >', null, 'Postal adress');
insert into metainfo values ('users', 'email', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:str\', >', null, 'E-mail');
insert into metainfo values ('users', 'telephone', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:str\', >', null, 'Telephone');
insert into metainfo values ('users', 'mobile', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:str\', >', null, 'Mobile phone');
insert into metainfo values ('users', 'fax', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:str\', >', null, 'Fax');

create table userabilities(
"user" integer references users,
ability text
);

insert into metainfo values ('userablities', 'user', '', 'users', 'Group');
insert into metainfo values ('userablities', 'ability', '', null, 'Ability');

create table customers(
id serial primary key,
organization integer references organizations, 
"user" integer references users
);
insert into metainfo values ('customers', null, null, null, '%(user.username)s (%(user.givenname)s %(user.surname)s) at %(organization.name)s');
insert into metainfo values ('customers', 'id', '<\'Class\', \'Grimoire.Utils:GenericWrapper Grimoire.Utils:Wrapper Grimoire.Types.Derived:SerialType\', >', null, 'Id');
insert into metainfo values ('customers', 'organization', '<\'GenericReferenceType\', \'organizations\')>', 'organizations', 'Organization');
insert into metainfo values ('customers', 'user', '<\'GenericReferenceType\', \'users\')>', 'users', 'User account');


create table producers(
id serial primary key,
name text,
contactperson integer references users,
note text /* till exempel för kontonummer och sånt */
);
insert into metainfo values ('producers', null, null, null, '%(name)s with contact %(contactperson.username)s (%(contactperson.givenname)s %(contactperson.surname)s)');
insert into metainfo values ('producers', 'id', '<\'Class\', \'Grimoire.Utils:GenericWrapper Grimoire.Utils:Wrapper Grimoire.Types.Derived:SerialType\', >', null, 'Id');
insert into metainfo values ('producers', 'name', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:unicode\', >', null, 'Name of the producer');
insert into metainfo values ('producers', 'contactperson', '<\'GenericReferenceType\', \'users\')>', 'users', 'Contact person');
insert into metainfo values ('producers', 'note', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:unicode\', >', null, 'Note');

create table productions(
id serial primary key,
name text, 
producer integer references producers, 
genre integer references genres
);
insert into metainfo values ('productions', null, null, null, '%(name)s by %(producer.name)s (%(genre.name)s)');
insert into metainfo values ('productions', 'id', '<\'Class\', \'Grimoire.Utils:GenericWrapper Grimoire.Utils:Wrapper Grimoire.Types.Derived:SerialType\', >', null, 'Id');
insert into metainfo values ('productions', 'name', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:unicode\', >', null, 'Name of the production');
insert into metainfo values ('productions', 'producer', '<\'GenericReferenceType\', \'producers\')>', 'producers', 'Producer');
insert into metainfo values ('productions', 'genre', '<\'GenericReferenceType\', \'genres\')>', 'genres', 'Genre');

create table shows(
id serial primary key,
production integer references productions,
customer integer references customers, 
showtype integer references showtypes, 
agegroup integer references agegroups, 
municipality integer references municipalities, 
cooptype integer references cooptypes, 
contractnumber serial, 
locationname text, 
ticketprice integer, 
tickets integer,
date date, 
time time,
spectators integer, 
state integer references showstates,
note text
);
insert into metainfo values ('shows', null, null, null, '%(production.producer.name)s: %(production.name)s at %(locationname)s at %(date)s %(time)s');
insert into metainfo values ('shows', 'id', '<\'Class\', \'Grimoire.Utils:GenericWrapper Grimoire.Utils:Wrapper Grimoire.Types.Derived:SerialType\', >', null, 'Id');
insert into metainfo values ('shows', 'production', '<\'GenericReferenceType\', \'productions\')>', 'productions', 'Production');
insert into metainfo values ('shows', 'customer', '<\'GenericReferenceType\', \'customers\')>', 'customers', 'Customer');
insert into metainfo values ('shows', 'showtype', '<\'GenericReferenceType\', \'showtypes\')>', 'showtypes', 'Type of show');
insert into metainfo values ('shows', 'agegroup', '<\'GenericReferenceType\', \'agegroups\')>', 'agegroups', 'Agegroup');
insert into metainfo values ('shows', 'municipality', '<\'GenericReferenceType\', \'municipalities\')>', 'municipalities', 'Municipality');
insert into metainfo values ('shows', 'cooptype', '<\'GenericReferenceType\', \'cooptypes\')>', 'cooptypes', 'Type of cooperation');
insert into metainfo values ('shows', 'contractnumber', '<\'Type\', \'__builtin__:object __builtin__:int\', >', null, 'Contract number');
insert into metainfo values ('shows', 'locationname', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:unicode\', >', null, 'Location of the performance');
insert into metainfo values ('shows', 'ticketprice', '<\'Type\', \'__builtin__:object __builtin__:int\', >', null, 'Ticketprice');
insert into metainfo values ('shows', 'tickets', '<\'Type\', \'__builtin__:object __builtin__:int\', >', null, 'Number of tickets');
insert into metainfo values ('shows', 'date', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:str\', >', null, 'Date');
insert into metainfo values ('shows', 'time', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:str\', >', null, 'Time');
insert into metainfo values ('shows', 'spectators', '<\'Type\', \'__builtin__:object __builtin__:int\', >', null, 'Number of spectators');
insert into metainfo values ('shows', 'state', '<\'GenericReferenceType\', \'showstates\')>', 'showstates', 'Current state');
insert into metainfo values ('shows', 'note', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:unicode\', >', null, 'Note');

create table projects(
id serial primary key,
name text, 
producer integer references producers, 
projecttype integer references projecttypes, 
cooptype integer references cooptypes
);
insert into metainfo values ('projects', null, null, null, '%(name)s by %(producer.name)s (%(projecttype.name)s %(cooptype.description)s)');
insert into metainfo values ('projects', 'id', '<\'Class\', \'Grimoire.Utils:GenericWrapper Grimoire.Utils:Wrapper Grimoire.Types.Derived:SerialType\', >', null, 'Id');
insert into metainfo values ('projects', 'name', '<\'Type\', \'__builtin__:object __builtin__:basestring __builtin__:unicode\', >', null, 'Project name');
insert into metainfo values ('projects', 'producer', '<\'GenericReferenceType\', \'producers\')>', 'producers', 'Producer');
insert into metainfo values ('projects', 'projecttype', '<\'GenericReferenceType\', \'projecttypes\')>', 'projecttypes', 'Type of project');
insert into metainfo values ('projects', 'cooptype', '<\'GenericReferenceType\', \'cooptypes\')>', 'cooptypes', 'Type of cooperation');

/* vilka productioner är med i vilka project? */
create table productioninprojects(
production integer references productions, 
project integer references projects
);
insert into metainfo values ('productioninprojects', null, null, null, '%(production.name)s is in %(project.name)');
insert into metainfo values ('productioninprojects', 'production', '<\'GenericReferenceType\', \'productions\')>', 'productions', 'Production');
insert into metainfo values ('productioninprojects', 'project', '<\'GenericReferenceType\', \'projects\')>', 'projects', 'Project');

/* vilka timmar har arbetats av vilka anställningsgrupper i vilket project? */
create table hours(
project integer references projects, 
employmentform integer references employmentforms, 
hours integer
);
insert into metainfo values ('hours', null, null, null, '%(hourses)s worked in %(project.name) in %(employmentform.description)s');
insert into metainfo values ('hours', 'projects', '<\'GenericReferenceType\', \'projects\')>', 'projects', 'Project');
insert into metainfo values ('hours', 'employmentform', '<\'GenericReferenceType\', \'employmentforms\')>', 'employmentforms', 'Form of empleyment');
insert into metainfo values ('hours', 'hours', '<\'Type\', \'__builtin__:object __builtin__:int\', >', null, 'Number of hours');



/* Fyll på med data */;

insert into lansmusikeninfo (
billingtime, 
account, 
address, 
zipcode, 
postaddress, 
email, 
telephone, 
fax
) 
values
(
30, '5555-665535', 'Musikvägen 1', '543 55', 'Östersund', 
'lansmusiken@jll.se', '063 44 343 22', '063 44 344 00'
);

insert into usergroups (name) values ('admin');
insert into usergroups (name) values ('producer');
insert into usergroups (name) values ('customer');

insert into organizationtypes (name) values ('Förskola');
insert into organizationtypes (name) values ('Kyrka');
insert into organizationtypes (name) values ('Landsting');
insert into organizationtypes (name) values ('Sjukhus/sjukhem');
insert into organizationtypes (name) values ('Folkhögskola');
insert into organizationtypes (name) values ('Förskola');
insert into organizationtypes (name) values ('6års/Låg');
insert into organizationtypes (name) values ('Lågstadium');
insert into organizationtypes (name) values ('Mellanstadium');
insert into organizationtypes (name) values ('Högstadium');
insert into organizationtypes (name) values ('Gymnasium');
insert into organizationtypes (name) values ('Särskola');
insert into organizationtypes (name) values ('Servicehus');
insert into organizationtypes (name) values ('Gruppboende/äldre');
insert into organizationtypes (name) values ('Daglig verksamhet/äldre');
insert into organizationtypes (name) values ('Kommun (Kultur/fritid mm)');
insert into organizationtypes (name) values ('Musikförening');
insert into organizationtypes (name) values ('Kultur- Hembygdsförening');
insert into organizationtypes (name) values ('Pensionärsförening');
insert into organizationtypes (name) values ('Enskild person/firma');
insert into organizationtypes (name) values ('Företag');
insert into organizationtypes (name) values ('Förening');
insert into organizationtypes (name) values ('Orkester');
insert into organizationtypes (name) values ('Kultur- Musikskola');

insert into genres (name) values('Konstmusik');
insert into genres (name) values('Nutida musik');
insert into genres (name) values('Folkmusik/världsmusik');
insert into genres (name) values('Jazz');
insert into genres (name) values('Visor/sånger');
insert into genres (name) values('Övrigt/blandat');

insert into regions (name) values('Utomlands');
insert into regions (name) values('Jämtland');
insert into regions (name) values('Härjedalen');
insert into regions (name) values('Ångermanland');
insert into regions (name) values('Medelpad');
insert into regions (name) values('Lappland');

insert into municipalities (name, region) values('Utomlands', 1);
insert into municipalities (name, region) values('Berg', 2);
insert into municipalities (name, region) values('Bräcke', 2);
insert into municipalities (name, region) values('Krokom', 2);
insert into municipalities (name, region) values('Ragunda', 2);
insert into municipalities (name, region) values('Strömsund', 2);
insert into municipalities (name, region) values('Åre', 2);
insert into municipalities (name, region) values('Östersund', 2);

insert into showtypes (description) values ('Offentlig');
insert into showtypes (description) values ('Skolkonsert lågstadium');
insert into showtypes (description) values ('Skolkonsert mellanstadium');
insert into showtypes (description) values ('Skolkonsert högstadium');
insert into showtypes (description) values ('Skolkonsert gymnasium');
insert into showtypes (description) values ('Konsert i vården/äldreomsorgen');
insert into showtypes (description) values ('Annan intern');

insert into showstates (description) values ('Preliminär');
insert into showstates (description) values ('Beställd');
insert into showstates (description) values ('Inställd');
insert into showstates (description) values ('Utförd');
insert into showstates (description) values ('Fakturerad');
insert into showstates (description) values ('Faktura betald');

insert into agegroups (description, lowerbound, upperbound) values('Barn', 0, 14);
insert into agegroups (description, lowerbound, upperbound) values('Ungdom', 15, 25);
insert into agegroups (description, lowerbound) values('Vuxna', 25);

insert into employmentforms (description) values ('Fast anställda musiker');
insert into employmentforms (description) values ('Frilansmusiker');
insert into employmentforms (description) values ('Producent/Konsulent');

insert into cooptypes (description) values ('Rikskonserter');
insert into cooptypes (description) values ('Annan regional musikverksamhet');
insert into cooptypes (description) values ('Annan kulturinstitution');
insert into cooptypes (description) values ('Kommun');
insert into cooptypes (description) values ('Övrigt');
