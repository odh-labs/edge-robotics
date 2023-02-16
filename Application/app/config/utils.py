import json

def read_json(json_file):
    with open(json_file, "r") as filename:
        j = json.load(filename)
    return j
