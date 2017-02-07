BEGIN TRANSACTION;
CREATE TABLE "operations" (
	`operation_id`	INTEGER,
	`name`	TEXT,
	`public_name`	TEXT,
	PRIMARY KEY(operation_id)
);
CREATE TABLE "keys" (
	`key`	TEXT UNIQUE,
	`permission_level`	INTEGER,
	`operation_id`	INTEGER,
	PRIMARY KEY(key)
	FOREIGN KEY(permission_level) REFERENCES permissions(level)
);
CREATE TABLE `permissions` (
	`level`	INTEGER,
	`name`	TEXT,
	PRIMARY KEY(level)
);
INSERT INTO `permissions` (level,name) VALUES (1,'customer'),
 (2,'auditor'),
 (3,'manager'),
 (4,'director'),
 (5,'master');
COMMIT;
