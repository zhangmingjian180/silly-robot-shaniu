import json
import yaml

def read_yaml(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

def read_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def write_json(data, filename):
    with open(filename, 'w') as f:
        return json.dump(data, f)

def add_to_json(data, filename):
    ori = read_json(filename)
    ori.extend(data)
    write_json(ori, filename)
