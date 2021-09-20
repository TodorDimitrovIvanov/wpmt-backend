BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "website" (
	"website_id"	text NOT NULL,
	"client_id"	text NOT NULL,
	"domain"	text NOT NULL,
	"domain_expiry"	date,
	"certificate"	text,
	"certificate_expiry"	date,
	PRIMARY KEY("website_id"),
	FOREIGN KEY("client_id") REFERENCES "users"("client_id")
);
CREATE TABLE IF NOT EXISTS "wordpress" (
	"website_id"	text NOT NULL,
	"url"	text NOT NULL,
	"path"	text,
	"version"	text NOT NULL,
	"plugins"	text,
	"themes"	text,
	"size"	text,
	"inodes"	text,
	FOREIGN KEY("website_id") REFERENCES "website"("website_id")
);
CREATE TABLE IF NOT EXISTS "backup" (
	"backup_id"	TEXT NOT NULL UNIQUE,
	"website_id"	TEXT,
	"host"	TEXT,
	"size"	TEXT,
	"date"	TEXT,
	"path"	TEXT,
	PRIMARY KEY("backup_id"),
	FOREIGN KEY("website_id") REFERENCES "website"("website_id")
);
CREATE TABLE IF NOT EXISTS "sftp" (
	"website_id"	TEXT NOT NULL,
	"host"	TEXT NOT NULL,
	"user"	TEXT NOT NULL,
	"pass"	TEXT NOT NULL,
	"port"	INTEGER NOT NULL,
	"path"	TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS "ssh" (
	"website_id"	integer NOT NULL,
	"host"	text NOT NULL,
	"user"	text NOT NULL,
	"pass"	text NOT NULL,
	"port"	INTEGER NOT NULL,
	"path"	text,
	FOREIGN KEY("website_id") REFERENCES "website"("website_id")
);
CREATE TABLE IF NOT EXISTS "ftp" (
	"website_id"	TEXT,
	"host"	TEXT NOT NULL,
	"user"	TEXT NOT NULL,
	"pass"	TEXT NOT NULL,
	"port"	INTEGER NOT NULL,
	"path"	TEXT,
	FOREIGN KEY("website_id") REFERENCES "website"("website_id")
);
CREATE TABLE IF NOT EXISTS "imap" (
	"website_id"	TEXT NOT NULL,
	"host"	TEXT NOT NULL,
	"user"	TEXT NOT NULL,
	"pass"	TEXT NOT NULL,
	"port"	INTEGER NOT NULL,
	"path"	TEXT,
	FOREIGN KEY("website_id") REFERENCES "website"("website_id")
);
CREATE TABLE IF NOT EXISTS "users" (
	"client_id"	text NOT NULL UNIQUE,
	"client_key"	text NOT NULL UNIQUE,
	"email"	text NOT NULL UNIQUE,
	"name"	text NOT NULL,
	"service"	text NOT NULL,
	"notifications"	INTEGER NOT NULL DEFAULT 1,
	"promos"	INTEGER NOT NULL DEFAULT 1,
	PRIMARY KEY("client_id")
);
COMMIT;
