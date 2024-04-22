-- create schema shutterfly;
-- use shutterfly;
SET FOREIGN_KEY_CHECKS = 0;
create table if not exists regions (
	region_id int primary key, -- could be auto_increment, but, i keep it as manually inserted for simplisity
    region_id_short_name varchar(20),
    region_name varchar(100),
    region_country varchar(100) -- this could be it's own table
);

truncate table regions;
insert into regions values
	(1, 'AK', 'Alaska', 'USA'),
	(2, 'VA', 'Virginia', 'USA');

create table if not exists cities (
	city_id int primary key,
    city_name varchar(100),
    region_id int,
    foreign key(region_id) references regions(region_id)
);
 
truncate table cities;
insert into cities values
	(1, 'Middletown', 1),
	(2, 'Farmington', 2);
    
create table if not exists customers (
    customer_id binary(12) primary key,
    created_at timestamp,
    updated_at timestamp,
    last_name varchar(150),
    adress_city int
);

truncate table customers;
insert into customers values
('96f55c7d8f42', '2017-01-06T12:46:46.384', Null, 'Smith', 1),
('96f55c7d8f41', '2017-01-06T12:46:46.384', Null, 'John', 2);

create table if not exists site_visits (
	customer_id binary(12),
    visit_time timestamp,
    page_id binary(12),
    tags json, -- can be set as an EAV is better search abilities are needed
    primary key (customer_id, visit_time),
    foreign key (customer_id) references customers(customer_id)
);

truncate table site_visits;
insert into site_visits values
	('96f55c7d8f42', '2017-01-06T12:45:52.041', 'ac05e815502f', '{"some key": "some value"}'),
	('96f55c7d8f42', '2017-01-03T12:45:52.041', 'ac05e815502f', '{"some key": "some value"}'),
	('96f55c7d8f42', '2017-01-20T12:45:52.041', 'ac05e815502a', '{"some key": "some value"}'),
	('96f55c7d8f41', '2017-01-06T12:45:52.041', 'ac05e815502g', '{"some key": "some value"}'),
	('96f55c7d8f41', '2017-02-15T12:45:52.041', 'ac05e815502s', '{"some key": "some value"}'),
	('96f55c7d8f41', '2017-02-06T13:45:52.041', 'ac03e415502s', '{"some key": "some value"}'),
	('96f55c7d8f41', '2017-02-20T12:45:52.041', 'ac05e815502s', '{"some key": "some value"}');

create table if not exists camera_makers (
	camere_maker_id int primary key,
    camera_maker_name varchar(50)
);

truncate table camera_makers;
insert into camera_makers values
	(1, 'Canon');

create table if not exists camera_model (
	camera_model_id int primary key,
    camere_maker_id int,
    camera_maker_name varchar(50),
    foreign key(camere_maker_id) references camera_makers(camere_maker_id)
);

truncate table camera_model;
insert into camera_model values
	(1, 1, 'EOS 80D');
    
create table if not exists images (
	image_id binary(12) primary key,
    customer_id binary(12),
    upload_time timestamp,
    camera_model_id int,
    foreign key(customer_id) references customers(customer_id),
    foreign key(camera_model_id) references camera_model(camera_model_id)
);

truncate table images;
insert into images values
	('d8ede43b1d9f', '96f55c7d8f42', '2017-01-06T12:47:12.344', 1),
    ('d8ede43b1d9e', '96f55c7d8f42', '2017-01-20T12:47:12.344', 1),
	('d8ede43b1d9g', '96f55c7d8f41', '2017-01-06T12:47:12.344', 1),
    ('d8ehe47b1d9h', '96f55c7d8f41', '2017-02-06T13:47:12.344', 1),
    ('d8eden3b1d9i', '96f55c7d8f41', '2017-02-15T12:47:12.344', 1);

create table if not exists orders (
	order_id binary(12),
    version int,
    order_time timestamp,
    customer_id binary(12),
    amount decimal(8,2),
    primary key (order_id, version),
    foreign key(customer_id) references customers(customer_id)
);

truncate table orders;
insert into orders values
	('68d84e5d1a43', 1, '2017-01-06T12:55:55.555', '96f55c7d8f42', 12.34),
    ('68d84e5d1a41', 1, '2017-01-20T12:55:55.555', '96f55c7d8f42', 40.34),
    ('68d84e5d4a44', 1, '2017-01-06T12:55:55.555', '96f55c7d8f41', 13.34),
    ('68d84e5j1a45', 1, '2017-02-15T12:55:55.555', '96f55c7d8f41', 17.34),
    ('68d84e8o1a45', 1, '2017-02-06T13:55:55.555', '96f55c7d8f41', 5.48),
    ('68d84e5j1a45', 2, '2017-02-20T12:55:55.555', '96f55c7d8f41', 21.16);

SET FOREIGN_KEY_CHECKS = 1;