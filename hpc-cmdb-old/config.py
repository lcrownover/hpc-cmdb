import os
import yaml

class AppConfig:
    def __init__(self, config_path: str = "/etc/hpc-cmdb/config.yaml" ):
        self.config_path = config_path
        self.api_users = []
        self.sqlite_path = ""

    def load(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(self.config_path)

        with open(self.config_path, "r") as f:
            config = yaml.safe_load(f)
            self.api_users = config["api_users"]
            self.sqlite_path = config["sqlite_path"]
