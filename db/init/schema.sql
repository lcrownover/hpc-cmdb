CREATE TABLE IF NOT EXISTS entries (
	entry_id serial PRIMARY KEY,
	name varchar (100) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS tags (
	tag_id serial PRIMARY KEY,
	name VARCHAR (40) NOT NULL,
	value VARCHAR (120) NOT NULL,
	UNIQUE(name, value)
);

CREATE TABLE IF NOT EXISTS entries_tags (
	entry_id serial NOT NULL REFERENCES entries (entry_id),
	tag_id serial NOT NULL REFERENCES tags (tag_id),
	UNIQUE(entry_id, tag_id)
);
