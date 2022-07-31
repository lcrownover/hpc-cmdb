from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
import psycopg2
import os
import logging
import sys
import re


def validate_name(name: str) -> str:
    valid_re = re.compile(r"^[a-zA-Z0-9-_]+$")
    if not valid_re.match(name):
        raise ValueError(f"Names must match pattern: {valid_re.pattern}")
    return name


class Tag(BaseModel):
    name: str
    value: str

    _validate_name = validator("name", allow_reuse=True)(validate_name)


class Entry(BaseModel):
    name: str
    tags: list[Tag] = []

    _validate_name = validator("name", allow_reuse=True)(validate_name)


class DuplicateEntryError(Exception):
    pass


class DuplicateTagError(Exception):
    pass


class EntryNotFoundError(Exception):
    pass


class TagNotFoundError(Exception):
    pass


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def li(msg: str):
    logging.info(f"\t{msg}")


def ld(msg: str):
    logging.debug(f"\t{msg}")


def lw(msg: str):
    logging.warning(f"\t{msg}")


db_username = os.getenv("DB_USERNAME")
db_password = os.getenv("DB_PASSWORD")
db_port = 5432
db_name = "cmdb"


origins = [
    "http://app:3000",
    "http://localhost:3000",
    "http://api:8000",
    "*",
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


try:
    conn = psycopg2.connect(
        database=db_name,
        user=db_username,
        password=db_password,
        host="db",
        port=db_port,
    )
except Exception as e:
    sys.stderr.write(f"Failed to connect to database. It might not be up yet.\n{e}\n")
    exit(1)

cur = conn.cursor()


def duplicate_tags_found(tags: list[Tag]) -> bool:
    return len(set([t.name for t in tags])) < 1


def db_get_entry_id(name: str) -> int:
    sql = "SELECT * FROM entries WHERE name = %s"
    cur.execute(sql, (name,))
    data = cur.fetchone()
    if data:
        ld(f"entry '{name}' exists")
        return data[0]
    ld(f"entry '{name}' doesnt exist")
    raise EntryNotFoundError


def db_get_tag_id(tag: Tag) -> int:
    sql = "SELECT * FROM tags WHERE name = %s AND value = %s"
    cur.execute(sql, (tag.name, tag.value))
    data = cur.fetchone()
    if data:
        ld(f"tag '{tag.name}:{tag.value}' exists")
        return data[0]
    ld(f"tag '{tag.name}:{tag.value}' doesnt exist")
    raise TagNotFoundError


def db_insert_entry(entry: Entry) -> int:
    try:
        entry_id = db_get_entry_id(entry.name)
    except:
        entry_id = None
    if entry_id:
        return entry_id
    li(f"inserting entry '{entry.name}'")
    sql = "INSERT INTO entries (name) VALUES (%s) RETURNING entry_id"
    cur.execute(sql, (entry.name,))
    entry_id = cur.fetchone()[0]
    conn.commit()
    return entry_id


def db_insert_tag(tag: Tag) -> int:
    try:
        tag_id = db_get_tag_id(tag)
    except:
        tag_id = None
    if tag_id:
        return tag_id
    li(f"inserting tag '{tag.name}:{tag.value}'")
    sql = "INSERT INTO tags (name, value) VALUES (%s, %s) RETURNING tag_id"
    cur.execute(sql, (tag.name, tag.value))
    tag_id = cur.fetchone()[0]
    conn.commit()
    return tag_id


def db_junction_exists(entry_id, tag_id) -> bool:
    sql = "SELECT * FROM entries_tags WHERE entry_id = %s AND tag_id = %s"
    cur.execute(sql, (entry_id, tag_id))
    data = cur.fetchone()
    if data:
        ld(f"junction '{entry_id} -> {tag_id}' exists")
        return True
    ld(f"junction '{entry_id} -> {tag_id}' doesnt exist")
    return False


def db_insert_junction(entry_id: int, tag_id: int):
    if db_junction_exists(entry_id, tag_id):
        return
    li(f"inserting junction '{entry_id} -> {tag_id}'")
    sql = "INSERT INTO entries_tags (entry_id, tag_id) VALUES (%s, %s)"
    cur.execute(sql, (entry_id, tag_id))
    conn.commit()


def db_remove_junction(entry_id: int, tag_id: int):
    if not db_junction_exists(entry_id, tag_id):
        return
    li(f"removing junction '{entry_id} -> {tag_id}'")
    sql = "DELETE FROM entries_tags WHERE entry_id = %s AND tag_id = %s"
    cur.execute(sql, (entry_id, tag_id))
    conn.commit()


def db_remove_tag_from_entry(entry: Entry, tag: Tag):
    entry_id = db_get_entry_id(entry.name)
    tag_id = db_get_tag_id(tag)
    db_remove_junction(entry_id, tag_id)


def db_get_all_entries() -> list[Entry]:
    entry_lookup = {}
    sql = """SELECT e.name, t.name, t.value
            FROM entries e
            INNER JOIN entries_tags et ON et.entry_id = e.entry_id
            INNER JOIN tags t ON et.tag_id = t.tag_id"""
    cur.execute(sql)
    data = cur.fetchall()
    if not data:
        raise EntryNotFoundError
    for row in data:
        ename, tname, tvalue = row
        if ename not in entry_lookup:
            entry_lookup[ename] = Entry(name=ename, tags=[])
        entry_lookup[ename].tags.append(Tag(name=tname, value=tvalue))
    return [e for e in entry_lookup.values()]


def db_get_entry(name: str) -> Entry:
    entry = Entry(name=name, tags=[])
    sql = """SELECT e.name, t.name, t.value
            FROM entries e
            INNER JOIN entries_tags et ON et.entry_id = e.entry_id
            INNER JOIN tags t ON et.tag_id = t.tag_id
            WHERE e.name = %s"""
    cur.execute(sql, (name,))
    data = cur.fetchall()
    if not data:
        return entry
    for row in data:
        entry.tags.append(Tag(name=row[1], value=row[2]))
    return entry


def db_delete_entry(name: str) -> Entry:
    entry = db_get_entry(name)
    if not entry:
        raise EntryNotFoundError
    entry_id = db_get_entry_id(name)
    if not entry_id:
        raise EntryNotFoundError
    j_sql = "DELETE FROM entries_tags WHERE entry_id = %s"
    cur.execute(j_sql, (entry_id,))
    conn.commit()
    e_sql = "DELETE FROM entries WHERE entry_id = %s"
    cur.execute(e_sql, (entry_id,))
    conn.commit()
    return entry


def db_add_tag_to_entry(entry: Entry, tag: Tag) -> Entry:
    ld(f"call add_tag_to_entry(entry={entry}, tag={tag})")
    for existing_tag in entry.tags:
        ld(f"existing_tag={existing_tag}")
        if existing_tag.name == tag.name and existing_tag.value != tag.value:
            li(f"overwriting '{tag.name}': '{existing_tag.value}' -> '{tag.value}'")
            db_remove_tag_from_entry(entry, existing_tag)
    entry_id = db_get_entry_id(entry.name)
    tag_id = db_insert_tag(tag)
    db_insert_junction(entry_id, tag_id)
    return db_get_entry(entry.name)


pre_data = [
    Entry(
        name="spiderman",
        tags=[
            Tag(name="realname", value="peter parker"),
            Tag(name="love-interest", value="mary jane watson"),
        ],
    ),
    Entry(
        name="superman",
        tags=[
            Tag(name="realname", value="clark kent"),
            Tag(name="love-interest", value="lois lane"),
        ],
    ),
]

# prepopulate data
for entry in pre_data:
    ld(f"populating pre_data: {entry}")
    try:
        entry_id = db_get_entry_id(entry.name)
    except EntryNotFoundError:
        entry_id = db_insert_entry(entry)
    if entry.tags:
        for tag in entry.tags:
            tag_id = db_insert_tag(tag)
            db_insert_junction(entry_id, tag_id)


###
#
# /entries -- POST new entry -- GET all entries -- DELETE error (dont want to delete everything)
#
@app.get("/entries/", response_model=list[Entry])
async def get_all_entries() -> list[Entry]:
    try:
        return db_get_all_entries()
    except:
        raise HTTPException(status_code=404, detail="No entries found")


@app.post("/entries/", response_model=Entry)
async def create_entry(entry: Entry) -> Entry:
    # check for duplicate tag names in the provided entry tags
    if duplicate_tags_found(entry.tags):
        raise HTTPException(
            status_code=500, detail=f"Duplicate name found in tag names"
        )

    # insert the entry, then get the existing entry back out
    # this is because you may post an entry with a single tag, but you should
    # get back the entry with all the existing tags as well
    db_insert_entry(entry)
    full_entry = db_get_entry(entry.name)

    # add all them tags
    for tag in entry.tags:
        full_entry = db_add_tag_to_entry(entry, tag)

    return full_entry


# @app.delete("/entries/")
# async def delete_all_entries() -> None:
#     # i don't like the idea of deleting everything with a single DELETE call to a single URL
#     raise HTTPException(status_code=500, detail="Unimplemented. Don't want to delete everything by mistake!")
#
###


###
#
#   /entries/{name}
#   POST error
#   GET entry
#   DELETE entry
#
@app.get("/entries/{name}/", response_model=Entry)
async def get_entry(name: str) -> Entry:
    try:
        return db_get_entry(name)
    except:
        raise HTTPException(status_code=404, detail="Entry not found")


@app.post("/entries/{name}/")
async def post_entry() -> None:
    raise HTTPException(
        status_code=500, detail="Use /entries/{name}/tags/ to manage tags."
    )


@app.delete("/entries/{name}/", response_model=Entry)
async def delete_entry(name: str) -> Entry:
    try:
        return db_delete_entry(name)
    except:
        raise HTTPException(status_code=404, detail="Entry not found")


#
###


###
#
#   /entries/{name}/tags
#   POST new tag for entry
#   GET all tags for entry
#   DELETE all tags for entry
#
@app.get("/entries/{name}/tags/", response_model=list[Tag])
async def get_tags(name: str):
    try:
        entry = db_get_entry(name)
    except:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry.tags


@app.post("/entries/{name}/tags/", response_model=Entry)
async def add_tag(name: str, tag: Tag):
    entry = db_add_tag_to_entry(db_get_entry(name), tag)
    return entry


# @app.delete("/entries/{name}/tags/")
# async def delete_all_tags_for_entry() -> None:
#     raise HTTPException(status_code=500, detail="Unimplemented. Don't want to delete everything by mistake!")
#
###


###
#
#   /entries/{name}/tags/{tag_name}
#   GET tag for entry
#   POST update tag data
#   DELETE tag on entry
#
@app.get("/entries/{name}/tags/{tag_name}/", response_model=Tag)
async def get_tag_for_entry(name: str, tag_name: str):
    entry = db_get_entry(name)
    for existing_tag in entry.tags:
        if tag_name == existing_tag.name:
            return existing_tag
    raise HTTPException(status_code=404, detail="Provided tag not found in entry")


@app.post("/entries/{name}/tags/{tag_name}/", response_model=Entry)
async def add_tag_to_entry(name: str, tag_name: str, tag: Tag):
    try:
        db_get_entry(name)
    except EntryNotFoundError:
        raise HTTPException(status_code=404, detail="Entry not found")
    if tag_name != tag.name:
        raise HTTPException(
            status_code=500, detail="Provided tag data does not match tag name in URL"
        )
    entry = db_add_tag_to_entry(db_get_entry(name), tag)
    return entry


@app.delete("/entries/{name}/tags/{tag_name}/")
async def delete_tag_from_entry(name: str, tag_name: str) -> Entry:
    try:
        entry = db_get_entry(name)
    except EntryNotFoundError:
        raise HTTPException(status_code=404, detail="Entry not found")
    for existing_tag in entry.tags:
        if existing_tag.name == tag_name:
            db_remove_tag_from_entry(entry, existing_tag)
    return db_get_entry(name)


#
###
