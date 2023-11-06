drop database if exists testdb2;
go
create database if not exists testdb2;
go
use testdb2;
go
create table if not exists users
(
    id bigint AUTO_INCREMENT not null,
    username varchar(255) not null unique,
    password varchar(255) not null,
    email varchar(255) not null unique,
    fullname varchar(255) not null,
    mobile varchar(255),
    email_verification_otp int,
    email_verification_date datetime,
    email_verification_status int,
    fp_verification_otp int,
    fp_verification_date datetime,
    fp_verification_status int,
    login_token varchar(500),
    login_token_date datetime,
    insert_date datetime not null default current_timestamp,
    active boolean not null default true,
    PRIMARY KEY (id)
);
go
create table if not exists employees
(
    id bigint AUTO_INCREMENT not null,
    user_id bigint,
    emp_code varchar(200) not null unique,
    name varchar(200) not null,
    designation varchar(200),
    profile varchar(200),
    created datetime not null default current_timestamp,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users(id) on delete cascade
);
go
create table if not exists logs
(
    id bigint AUTO_INCREMENT not null,
    action Text,
    ip_address varchar(200),
    req_header Text,
    browser varchar(200),
    platform varchar(200),
    mobile varchar(200),
    referer varchar(200),
    city varchar(200),
    country varchar(200),
    region varchar(200),
    latitude varchar(200) ,
    longitude varchar(200),
    timezone varchar(200),
    log_date datetime not null default current_timestamp,
    called_api varchar(200),
    user_id varchar(200),
    emp_id varchar(200),
    req_data Text,
    PRIMARY KEY (id)
);