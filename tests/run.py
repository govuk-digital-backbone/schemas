import json

from glob import glob
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError

from referencing import Registry, Resource
from referencing.exceptions import NoSuchResource

SCHEMAS = Path("../schemas")


def retrieve_from_filesystem(uri: str):
    # remove any scheme or authority from the URI
    if "://" in uri:
        uri = uri.split("://", 1)[1]
    if "/" in uri:
        uri = uri.split("/", 1)[1]
    if not uri.endswith(".json"):
        uri += ".json"
    
    path = SCHEMAS / Path(uri)
    contents = json.loads(path.read_text())
    return Resource.from_contents(contents)


def validate(data: dict, schema_name: str):
    registry = Registry(retrieve=retrieve_from_filesystem)
    Draft202012Validator(
        {"$ref": schema_name},
        registry=registry,
    ).validate(data)
    return True


def main():
    files = glob("*.json")
    for file in sorted(files):
        # split file by underscore and take the first part as schema name
        test_key = file.split(".")[0]
        test_id, schema_name, desired_outcome = test_key.split("_")
        try:
            data = json.loads(Path(file).read_text())
            if validate(data, schema_name):
                if desired_outcome == "pass":
                    print(f"Test {test_key} passed.")
                else:
                    print(f"Test {test_key} failed: expected invalid but got valid.")
        except ValidationError as e:
            if desired_outcome == "fail":
                print(f"Test {test_key} passed: caught expected validation error - {e.message}")
            else:
                print(f"Test {test_key} failed: unexpected validation error - {e.message}")
        except Exception as e:
            raise e

if __name__ == "__main__":
    main()
