BEGIN TRANSACTION;
DROP TABLE IF EXISTS "website";
CREATE TABLE IF NOT EXISTS "website" (
	"website_id"	text NOT NULL,
	"client_id"	text NOT NULL,
	"domain"	text NOT NULL,
	"domain_expiry"	date,
	"certificate"	text,
	"certificate_expiry"	date,
	FOREIGN KEY("client_id") REFERENCES "users"("client_id"),
	PRIMARY KEY("website_id")
);
DROP TABLE IF EXISTS "wordpress";
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
DROP TABLE IF EXISTS "accounts";
CREATE TABLE IF NOT EXISTS "accounts" (
	"account_id"	TEXT NOT NULL,
	"website_id"	TEXT NOT NULL,
	"type"	TEXT NOT NULL,
	"hostname"	TEXT NOT NULL,
	"username"	TEXT NOT NULL,
	"password"	TEXT NOT NULL,
	"port"	INTEGER NOT NULL,
	"path"	TEXT,
	FOREIGN KEY("website_id") REFERENCES "wordpress"("website_id"),
	PRIMARY KEY("account_id")
);
DROP TABLE IF EXISTS "users";
CREATE TABLE IF NOT EXISTS "users" (
	"client_id"	text NOT NULL UNIQUE,
	"client_key"	text NOT NULL UNIQUE,
	"email"	text NOT NULL UNIQUE,
	"name"	text NOT NULL,
	"service"	text NOT NULL,
	"notifications"	INTEGER NOT NULL DEFAULT 1,
	"promos"	INTEGER NOT NULL DEFAULT 1,
	"state"	TEXT,
	PRIMARY KEY("client_id")
);
DROP TABLE IF EXISTS "backup";
CREATE TABLE IF NOT EXISTS "backup" (
	"backup_id"	TEXT NOT NULL UNIQUE,
	"website_id"	TEXT NOT NULL,
	"account_id"	TEXT NOT NULL,
	"data"	TEXT,
	FOREIGN KEY("website_id") REFERENCES "website"("website_id"),
	FOREIGN KEY("account_id") REFERENCES "accounts",
	PRIMARY KEY("backup_id")
);
DROP TABLE IF EXISTS "transfer";
CREATE TABLE IF NOT EXISTS "transfer" (
	"transfer_id"	TEXT NOT NULL,
	"website_id"	TEXT NOT NULL,
	"source_account_id"	TEXT NOT NULL,
	"target_account_id"	TEXT NOT NULL,
	"status"	TEXT NOT NULL,
	"data"	TEXT,
	FOREIGN KEY("target_account_id") REFERENCES "accounts"("account_id"),
	FOREIGN KEY("website_id") REFERENCES "website"("website_id"),
	FOREIGN KEY("source_account_id") REFERENCES "accounts"("account_id"),
	PRIMARY KEY("transfer_id")
);
COMMIT;
