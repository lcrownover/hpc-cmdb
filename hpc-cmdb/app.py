import logging
import sqlite3
from .config import AppConfig
from .database import NodeDB

from flask import Flask, jsonify, request
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
auth = HTTPBasicAuth()

# logging.basicConfig(
#     filename="hpc-cmdb.log",
#     level=logging.DEBUG,
#     format="%(asctime)s %(levelname)s %(name)s : %(message)s",
# )

# if __name__ != "__main__":
#     gunicorn_logger = logging.getLogger("gunicorn.error")
#     app.logger.handlers = gunicorn_logger.handlers
#     app.logger.setLevel(gunicorn_logger.level)


debug_config_path = "config.yaml"


config = AppConfig(config_path=debug_config_path)
config.load()

node_db = NodeDB(config.sqlite_path)


@auth.verify_password
def verify_password(username, password):
    for authpair in config.api_users:
        if authpair["username"] == username:
            if authpair["password"] == password:
                return username


@app.route("/api/v1/status")
@auth.login_required
def status():
    return jsonify({"status": "OK"})

@app.route("/api/v1/talapas/nodes")
@auth.login_required
def nodes():
    return jsonify(node_db.get_nodes())

@app.route("/api/v1/talapas/nodes/<hostname>", methods=['POST', 'GET'])
@auth.login_required
def node(hostname):
    if request.method == "POST":
        data = request.get_json()
        ipaddress = data["ipaddress"]
        node_db.add_node(hostname, ipaddress)
        return jsonify(data)
    else: # GET
        return jsonify(node_db.get_node(hostname))



if __name__ == "__main__":
    app.run()
