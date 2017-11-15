from argparse import ArgumentParser

import pkg_resources
import gzip
import json
from datetime import datetime
from bson import json_util

from smug.connection_manager import ConnectionManager


class GzImporter:
    def __init__(self, connection_mananger):
        self.connection_manager = connection_mananger

    def process_files(self, files, large_analyses=False):
        for file in files:
            self.process_file(file, large_analyses)

    def process_file(self, file, large_analyses=False):
        filename = pkg_resources.resource_filename('resources', file)

        with gzip.open(filename, 'rt') as f:
            print('Sending {}'.format(file))
            for index, content in enumerate(f.readlines()):
                if large_analyses:
                    if index % 10 != 0:
                        continue
                original_message = json.loads(content)

                formatted_message = {
                    'message': original_message['text'],
                    'author': original_message['user']['name'],
                    'metadata': {
                        'date': datetime.fromtimestamp(int(original_message['timestamp_ms']) / 1000),
                        'url': original_message['id'],
                        'type': 'post',
                    }
                }
                self.connection_manager.publish_to_queue('clean',
                                                         json.dumps(formatted_message, default=json_util.default))


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--files', nargs='+')

    args = parser.parse_args()
    files = args.files

    files = [resource for resource in pkg_resources.resource_listdir('resources', '') if ".gz" in resource]

    connection_manager = ConnectionManager()
    csv_importer = GzImporter(connection_manager)
    csv_importer.process_files(files=files, large_analyses=True)
    exit(0)
