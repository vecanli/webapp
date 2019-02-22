drop table if exists user;
create table user(
	id integer primary key autoincrement,
	username char(64) not null unique,
	password char(128) not null
); 

drop table if exists history;
create table history(
	 id integer primary key autoincrement,
	 user_id integer not null,
	 stock_code char(64) not null,
	 result char(256) not null,
	 query_time datatime not null
);