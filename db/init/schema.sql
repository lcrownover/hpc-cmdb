CREATE TABLE IF NOT EXISTS entries (
	entry_id serial PRIMARY KEY,
	hostname varchar (100) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS tags (
	tag_id serial PRIMARY KEY,
	tag_name VARCHAR (40) NOT NULL,
	tag_value VARCHAR (120) NOT NULL,
	UNIQUE(tag_name, tag_value)
);

CREATE TABLE IF NOT EXISTS entries_tags (
	entry_id serial NOT NULL REFERENCES entries (entry_id),
	tag_id serial NOT NULL REFERENCES tags (tag_id),
	UNIQUE(entry_id, tag_id)
);
