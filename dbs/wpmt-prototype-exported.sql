CREATE TABLE users ( 
	client_id            text NOT NULL  PRIMARY KEY  ,
	client_key           text NOT NULL    ,
	email                text NOT NULL    ,
	name                 text NOT NULL    ,
	service              text NOT NULL    ,
	notifications        text NOT NULL DEFAULT disabled   ,
	icon                 text     
 );

CREATE TABLE website ( 
	website_id           text NOT NULL  PRIMARY KEY  ,
	client_id            text NOT NULL    ,
	domain               text NOT NULL    ,
	domain_expiry        date     ,
	certificate          text     ,
	certificate_expiry   date     ,
	FOREIGN KEY ( client_id ) REFERENCES users( client_id )  
 );

CREATE TABLE wordpress ( 
	website_id           text NOT NULL    ,
	url                  text NOT NULL    ,
	path                 text     ,
	version              text NOT NULL    ,
	plugins              text     ,
	themes               text     ,
	size                 text     ,
	inodes               text     ,
	FOREIGN KEY ( website_id ) REFERENCES website( website_id )  
 );

CREATE TABLE ssh ( 
	website_id           integer NOT NULL    ,
	host                 text NOT NULL    ,
	user                 text NOT NULL    ,
	pass                 text NOT NULL    ,
	port                 text NOT NULL    ,
	path                 text     ,
	FOREIGN KEY ( website_id ) REFERENCES website( website_id )  
 );

