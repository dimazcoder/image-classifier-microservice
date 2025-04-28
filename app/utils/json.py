import json
import re


def get_json_from_text(text, json_pattern=None):
    if not text:
        return None
    json_pattern = r'```json\n(.*?)\n```' if not json_pattern else json_pattern
    match = re.search(json_pattern, text, re.DOTALL)
    if match:
        return match.group(1)
    return None


def validate_json(json_str):
    if not json_str:
        return False
    try:
        parsed_json = json.loads(json_str)
        return parsed_json
    except json.JSONDecodeError as e:
        return False


def repair_json(json_str):
    if not json_str:
        return False
    json_str = re.sub(r'[^\S\n]+', '', json_str)
    json_str = json_str.replace('""', '":"')
    json_str = json_str.replace('"\n', '",\n')
    json_str = json_str.replace('}\n', '},\n')
    json_str = json_str.replace('",\n}', '"\n}')
    json_str = json_str.replace('},\n]', '}\n]')
    return validate_json(json_str)


def sanitize_json(json_str):
    control_chars = ''.join(map(chr, range(0, 32)))  # Characters from U+0000 to U+001F
    control_chars += ''.join(map(chr, range(127, 160)))  # Characters from U+007F to U+009F
    control_char_re = re.compile(f'[{re.escape(control_chars)}]')

    json_str = json_str.replace('\\', '\\\\').replace('"', '\\"')
    json_str = control_char_re.sub('', json_str)
    json_str = re.sub(r'\s+', ' ', json_str)

    return json_str

def json_use_func(json_obj, func):
    if isinstance(json_obj, dict):
        return {key: json_use_func(value, func) for key, value in json_obj.items()}
    elif isinstance(json_obj, list):
        return [json_use_func(element, func) for element in json_obj]
    elif isinstance(json_obj, str):
        return func(json_obj)
    else:
        return json_obj
