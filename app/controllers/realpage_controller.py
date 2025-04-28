import os
import shutil

from app.core.config import config
from app.services.realpage_service import RealpageService
from app.utils.file_manager import prep_filename


class RealpageController:
    def __init__(self):
        self.base_directory = os.path.join(config.static_path, 'realpage')

    def test(self, query):
        test_filepath = os.path.join(self.base_directory, 'test.pdf')

        service = RealpageService()
        response = service.find_in_file(
            open(test_filepath, "rb"),
            query
        )
        return response


    def process_local_files(self):
        source_directory = os.path.join(self.base_directory, 'source')
        working_directory = os.path.join(self.base_directory, 'results')
        submarkets_directory = os.path.join(self.base_directory, 'submarkets')

        reader_service = RealpageService()
        for filename in os.listdir(source_directory):
            if not filename.endswith('.pdf'):
                continue

            filepath = os.path.join(source_directory, filename)
            basename, extension = os.path.splitext(filename)

            reader_service.output_directory(
                os.path.join(working_directory, prep_filename(basename))
            )

            processed = reader_service.read(
                file=open(filepath, "rb"),
                submarkets_directory=submarkets_directory

            )

            if processed:
                dest_path = os.path.join(self.base_directory, 'processed')
            else:
                dest_path = os.path.join(self.base_directory, 'incomplete')

            os.makedirs(dest_path, exist_ok=True)
            shutil.move(filepath, os.path.join(dest_path, filename))
