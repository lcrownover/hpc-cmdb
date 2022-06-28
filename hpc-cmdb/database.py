import sqlite3

class CMDBCursor:
    def __init__(self, sqlite_path: str):
        self.sqlite_path = sqlite_path

    def __enter__(self):
        self.con = sqlite3.connect(self.sqlite_path)
        return self.con.cursor()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.con.commit()
        self.con.close()


class NodeDB:
    def __init__(self, sqlite_path: str):
        self.path = sqlite_path
        with CMDBCursor(self.path) as cur:
            cur.execute("CREATE TABLE IF NOT EXISTS nodes (hostname, ipaddress, UNIQUE (hostname))")

    def get_nodes(self):
        nodes = []
        with CMDBCursor(self.path) as cur:
            cur.execute(f"SELECT * FROM nodes")
            records = cur.fetchall()
            for record in records:
                nodes.append({"hostname": record[0], "ipaddress": record[1]})
            return nodes

    def get_node(self, hostname: str):
        with CMDBCursor(self.path) as cur:
            cur.execute("SELECT * FROM nodes WHERE hostname = ?", [ hostname ])
            records = cur.fetchall()
            return {"hostname": records[0][0], "ipaddress": records[0][1]}

    def add_node(self, hostname: str, ipaddress: str):
        with CMDBCursor(self.path) as cur:
            cur.execute("INSERT OR REPLACE INTO nodes (hostname, ipaddress) VALUES (?, ?)", [hostname, ipaddress])

