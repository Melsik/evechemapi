BEGIN TRANSACTION;
CREATE TABLE "operations" (
	`operation_id`	INTEGER,
	`name`	TEXT,
	`public_name`	TEXT,
	PRIMARY KEY(operation_id)
);
CREATE TABLE "keys" (
	`key`	TEXT UNIQUE,
	`access_level`	INTEGER,
	`operation_id`	INTEGER,
	PRIMARY KEY(key)
	FOREIGN KEY(operation_id) REFERENCES operations(operation_id)
	FOREIGN KEY(access_level) REFERENCES access_levels(access_level)
);
CREATE TABLE `access_levels` (
	`access_level`	INTEGER,
	`access_string`	TEXT,
	PRIMARY KEY(access_level)
);
INSERT INTO `access_levels` (access_level,access_string) VALUES (1,'customer'),
 (2,'auditor'),
 (3,'manager'),
 (4,'director'),
 (5,'master');
COMMIT;
