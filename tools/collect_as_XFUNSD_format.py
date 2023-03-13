import json
import os
from tqdm import tqdm
import random
import string

def generate_json(*, json_path: str, json_number: str, dict: dict):

    json_object = json.dumps(dict, indent=4)
    json_name = os.path.join(json_path, "".join([json_number, ".json"]))

    with open(json_name, "w") as outfile:
        outfile.write(json_object)


def get_random_string():
    
    length = 10
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

file_path = os.path.join(os.getcwd(), "funsd_structure", "testing_data", "annotations")

new_json = {}
new_json["lang"] = "es"
new_json["version"] = "0.1"
new_json["split"] = "train"

dicts_list = []

print(os.path.isdir(file_path))
if os.path.isdir(file_path):
    for file in tqdm(sorted(os.listdir(file_path))):
        if file.endswith(".json"):

            with open(os.path.join(file_path, file), 'r') as openfile:
                json_object = json.load(openfile)

            interior = {}
            fname = "".join([file[:-5], ".png"])
            interior["fname"] = fname
            interior["width"] = 1654
            interior["height"] = 2339

            intermediate = {}
            intermediate["id"] = file[:-5]
            intermediate["uid"] = get_random_string()
            intermediate["document"] = json_object["form"]
            intermediate["img"] = interior
            dicts_list.append(intermediate)

new_json["documents"] = dicts_list
generate_json(json_path=os.getcwd(), json_number="es_val", dict=new_json)