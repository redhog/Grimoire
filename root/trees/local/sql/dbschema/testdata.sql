delete from shows;
delete from productions;
delete from producers;
delete from customers;
delete from organizations;
delete from users;
delete from userabilities;
delete from groupabilities;

insert into users (
usergroup, givenname, surname, username, password, address, zipcode,postaddress, email, mobile
) 
values (
3, 'Bo', 'Öhrman', 'bo', 'o', 'Finvägen 23', '543 45', 'Östersund', 'bo.ohrman@jll.se', '0744 433 433 44'
);
insert into users (
usergroup, givenname, surname, username, password, address, zipcode,postaddress, email, mobile
) 
values (
3, 'Bengt', 'Beställare', 'bengt', 'b', 'Govägen 2', '543 45', 'Östersund', 'b.customer@best.se', '0744 433 433 44'
);
insert into users (
usergroup, givenname, surname, username, password, address, zipcode,postaddress, email, mobile
) 
values (
2, 'Per', 'Producent', 'per', 'p', 'Mjukvägen 6', '543 45', 'Krokom', 'p.producer@prod.se', '0744 433 433 44'
);

insert into organizations (address, zipcode, postaddress, organizationtype)
values ('Krokomsvägen 1', '453 64', 'Krokom', 1);

insert into customers (organization, "user")
values (1, 1);

insert into producers (name, contactperson, note)
values ('Pelles Produktioner AB', 2, 'bankgiro 677 454 23');

insert into productions (name, producer, genre) 
values('Pelle Plutt på nya äventyr', 1, 5);


insert into shows(
production,
customer, 
showtype, 
municipality, 
locationname, 
ticketprice, 
tickets, 
date, 
time, 
spectators,
state
) values (
1, 1, 1, 1, 'Krokomsskolan', 60, 200, '2004-03-03', '18:30', 4711, 1
);

/* admin abilities */
insert into groupabilities(usergroup, ability) values (1, 'update');
insert into groupabilities(usergroup, ability) values (1, 'list');
insert into groupabilities(usergroup, ability) values (1, 'type');
insert into groupabilities(usergroup, ability) values (1, 'create');

/* producer abilities */
insert into groupabilities(usergroup,ability) values (2, 'update.productions');
insert into groupabilities(usergroup,ability) values (2, 'create.productions');
insert into groupabilities(usergroup,ability) values (2, 'update.shows');
insert into groupabilities(usergroup,ability) values (2, 'create.shows');
insert into groupabilities(usergroup,ability) values (2, 'update.own');

/* customer abilities */
insert into groupabilities(usergroup, ability) values (3, 'update.shows.');
insert into groupabilities(usergroup, ability) values (3, 'update.own');


