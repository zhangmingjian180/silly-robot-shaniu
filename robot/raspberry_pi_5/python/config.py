import yaml
from pyaml_env import parse_config

def read_yaml(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

config = parse_config("config.yaml")
