import json
import logging
import os
import re


def prep_filename(filename):
    filename = re.sub(r'[^a-zA-Z0-9-_\s]+', '', filename)
    filename = re.sub(r'\s+', '_', filename)
    return filename.lower()


class FileManager:
    def __init__(self, working_directory):
        self.working_directory = self.set_working_directory(
            working_directory
        )

    def set_working_directory(self, path):
        if not path:
            raise ValueError("Directory cannot be empty")

        if not os.path.exists(path):
            os.makedirs(path)

        return path

    def prep_path(self, filename, directory=None):
        path = self.working_directory
        filename = prep_filename(filename)

        if directory:
            directory = prep_filename(directory)
            path = os.path.join(path, directory)
            if not os.path.exists(path):
                os.makedirs(path)

        return os.path.join(path, filename)

    def get_path(self, directory=None):
        path = self.working_directory
        if directory:
            directory = prep_filename(directory)
            path = os.path.join(path, directory)
        return path

    def save_text(self, content, filename, directory=None):
        path = self.prep_path(
            filename, directory
        )
        try:
            with open(path + '.txt', 'w') as file:
                file.write(content)
        except Exception as e:
            print(f"Error writing text to file '{path}': {e}")

    def save_json(self, content, filename, directory=None):
        path = self.prep_path(
            filename, directory
        )
        try:
            with open(path + '.json', 'w') as file:
                json.dump(content, file, indent=4)
        except Exception as e:
            print(f"Error writing text to file '{path}': {e}")

    def read_files(self, directory=None, extension=".json"):
        files_content = {}
        path = self.working_directory
        if directory:
            directory = prep_filename(directory)
            path = os.path.join(path, directory)

        for file_name in os.listdir(path):
            if file_name.endswith(extension) or not extension:
                file_path = os.path.join(path, file_name)
                file_name_without_extension = os.path.splitext(file_name)[0]
                with open(file_path, 'r') as file:
                    try:
                        if extension == ".json":
                            file_content = json.load(file)
                        else:
                            file_content = file.read()
                        files_content[file_name_without_extension] = file_content
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON file '{file_name}': {e}", flush=True)
        return files_content

    def file_exists(self, filename, directory=None):
        path = self.prep_path(
            filename, directory
        )

        try:
            with open(path+'.json', 'r') as file:
                content = json.load(file)
            return content
        except FileNotFoundError:
            return False
