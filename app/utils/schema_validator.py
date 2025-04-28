from pydantic import ValidationError, BaseModel


def object_validator(schema, json_object: dict):
    try:
        schema(**json_object)
        return json_object
    except ValidationError as e:
        return False


def list_validator(schema, json_object: list):
    try:
        schema(list=json_object)
        return json_object
    except ValidationError as e:
        return False
