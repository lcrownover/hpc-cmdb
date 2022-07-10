from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import os
import logging
import sys


class Tag(BaseModel):
    name: str
    value: str


class Entry(BaseModel):
    name: str
    tags: list[Tag] | None = None


logging.basicConfig(stream=sys.stdout, level=logging.INFO)


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

app = FastAPI()

conn = psycopg2.connect(
    database=db_name,
    user=db_username,
    password=db_password,
    host="cmdb-db",
    port=db_port,
)
cur = conn.cursor()


def db_get_entry_id(name: str) -> int | None:
    sql = "SELECT * FROM entries WHERE name = %s"
    cur.execute(sql, (name,))
    data = cur.fetchone()
    if data:
        ld(f"entry '{name}' exists")
        return data[0]
    ld(f"entry '{name}' doesnt exist")
    return None


def db_get_tag_id(tag: Tag) -> int | None:
    sql = "SELECT * FROM tags WHERE name = %s AND value = %s"
    cur.execute(sql, (tag.name, tag.value))
    data = cur.fetchone()
    if data:
        ld(f"tag '{tag.name}:{tag.value}' exists")
        return data[0]
    ld(f"tag '{tag.name}:{tag.value}' doesnt exist")
    return None


def db_insert_entry(entry: Entry) -> int:
    entry_id = db_get_entry_id(entry.name)
    if entry_id:
        return entry_id
    li(f"inserting entry '{entry.name}'")
    sql = "INSERT INTO entries (name) VALUES (%s) RETURNING entry_id"
    cur.execute(sql, (entry.name,))
    entry_id = cur.fetchone()[0]
    conn.commit()
    return entry_id


def db_insert_tag(tag: Tag):
    tag_id = db_get_tag_id(tag)
    if tag_id:
        return tag_id
    li(f"inserting tag '{tag.name}:{tag.value}'")
    sql = "INSERT INTO tags (name, value) VALUES (%s, %s) RETURNING tag_id"
    cur.execute(sql, (tag.name, tag.value))
    tag_id = cur.fetchone()[0]
    conn.commit()
    return tag_id


def db_junction_exists(entry_id, tag_id) -> bool:
    sql = "SELECT 1 FROM entries_tags WHERE entry_id = %s AND tag_id = %s"
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


pre_data = [
    Entry(
        name="spiderman",
        tags=[
            Tag(name="realname", value="peter parker"),
            Tag(name="love interest", value="mary jane watson"),
        ],
    ),
    Entry(
        name="superman",
        tags=[
            Tag(name="realname", value="clark kent"),
            Tag(name="love interest", value="lois lane"),
        ],
    ),
]

# prepopulate data
for entry in pre_data:
    entry_id = db_insert_entry(entry)
    if entry.tags:
        for tag in entry.tags:
            tag_id = db_insert_tag(tag)
            db_insert_junction(entry_id, tag_id)


@app.get("/entries/", response_model=list[Entry])
async def get_all_entries():
    # TODO(lcrown): write the select statements to get all the entries and format them correctly
    return pre_data


@app.post("/entries/", response_model=Entry)
async def create_entry(entry: Entry):
    entry_id = db_insert_entry(entry)
    if entry.tags:
        for tag in entry.tags:
            tag_id = db_insert_tag(tag)
            db_insert_junction(entry_id, tag_id)
    return entry


@app.get("/entries/{name}/tags/", response_model=list[Tag])
async def get_tags(name: str):
    entry_id = db_get_entry_id(name)
    if not entry_id:
        raise HTTPException(status_code=404, detail="Entry not found")
    # TODO(lcrown): need to return list of tags here
    return


@app.get("/entries/{name}/", response_model=Entry)
async def get_entry(name: str):
    for entry in pre_data:
        if entry.name == name:
            return entry
    raise HTTPException(status_code=404, detail="Not found")
