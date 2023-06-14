import csv, json, os
import pandas as pd


def path_exists(*path):
    path = os.path.join(*path)
    return os.path.exists(path)


def create_directory(path):
    os.makedirs(path, exist_ok=True)


def read_csv(*path):
    path = os.path.join(*path)
    return pd.read_csv(path)


def dict_to_json_file(path, dict):
    with open(path, "w") as outfile:
        json.dump(dict, outfile, default=lambda x: x.__dict__)


def csv_to_arr(path):
    arr = []
    with open(path) as csvFile:
        csvReader = csv.DictReader(csvFile)
        for csvRow in csvReader:
            obj = {fieldname: value.strip() for (fieldname, value) in csvRow.items()}
            arr.append(obj)
    return arr


def arr_to_json_file(path, arr):
    with open(path, "w") as outfile:
        json.dump(arr, outfile)


def read_first_line(path) -> str:
    with open(path, "r") as f:
        line = f.readline()
    return line


def get_files_in_directory(path) -> list:
    return os.listdir(path)


def set_json_property(path, property, value):
    with open(path, "r") as jsonFile:
        data = json.load(jsonFile)

    data[property] = value

    with open(path, "w") as jsonFile:
        json.dump(data, jsonFile)
