import hashlib
import logging
from datetime import datetime
import os
import random
import string
import uuid
from typing import List, Any


def gen_kebab_name(block_len=4, n_blocks=3) -> str:
    return gen_random_name(block_len=4, n_blocks=3, delimiter='-')

def gen_snake_name(block_len=4, n_blocks=3) -> str:
    return gen_random_name(block_len=4, n_blocks=3, delimiter='_')

def gen_random_name(block_len=4, n_blocks=3, delimiter='') -> str:
    def generate_random_string(length):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    return delimiter.join(generate_random_string(block_len) for _ in range(n_blocks))


def write_traceback(traceback_info):
    timestamp = datetime.now().strftime("%Y%m%d%-H%M%S")
    traceback_file = os.path.join("traceback", f"{timestamp}_{uuid.uuid4()}.txt")
    with open(traceback_file, "w+") as file:
        file.write(traceback_info)
    logging.info(f"Traceback information saved to '{traceback_file}'")


def prep_hash(data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    elif not isinstance(data, (bytes, bytearray)):
        raise TypeError("data must be a string or bytes-like object")

    hasher = hashlib.sha256()
    hasher.update(data)
    return hasher.hexdigest()

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]