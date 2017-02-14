BEGIN TRANSACTION;
CREATE TABLE `permissions` (
	`name`	TEXT,
	PRIMARY KEY(name)
);
INSERT INTO `permissions` (name) VALUES ('customer'),
 ('auditor'),
 ('manager'),
 ('director'),
 ('master');
CREATE TABLE "operations" (
	`id`	INTEGER,
	`name`	TEXT,
	`public_name`	TEXT,
	PRIMARY KEY(id)
);
CREATE TABLE "keys" (
	`value`	TEXT UNIQUE,
	`permission`	TEXT,
	`operation_id`	INTEGER,
	`name`	TEXT,
	PRIMARY KEY(value)
	FOREIGN KEY(operation_id) REFERENCES operations(id)
);

/* Tower Application Tables */
CREATE TABLE `towers` (
	`id`	INTEGER,
	`op_id` INTEGER,
	`type`	INTEGER,
	`system`	TEXT,
	`planet`	INTEGER,
	`moon`	INTEGER,
	`name`	TEXT,
	`online`	INTEGER,
	`sov`	INTEGER,
	`cycles_at`	TEXT,
	`stront_count`	INTEGER,
	`fuel_count`	INTEGER,
	`fuel_last_update`	INTEGER,
	PRIMARY KEY(id)
	FOREIGN KEY(op_id) REFERENCES operations(id)
);
CREATE TABLE "processes" (
	`id`	INTEGER,
	`tower_id`	INTEGER,
	PRIMARY KEY(id)
	FOREIGN KEY(tower_id) REFERENCES towers(id)
);
CREATE TABLE "equipment" (
	`id`	INTEGER,
	`type` INTEGER,
	`name` TEXT,
	`process_id`	INTEGER,
	`last_updated`	INTEGER,
	`resource`	INTEGER,
	`contains`	INTEGER,
	`online` INTEGER,
	PRIMARY KEY(id)
	FOREIGN KEY(process_id) REFERENCES processes(id)
);
CREATE TABLE "links" (
	`target`	INTEGER,
	`source`	INTEGER,
	`resource`	INTEGER,
	PRIMARY KEY(target,source,resource)
	FOREIGN KEY(source) REFERENCES equipment(id)
	FOREIGN KEY(target) REFERENCES equipment(id)
);



COMMIT;
