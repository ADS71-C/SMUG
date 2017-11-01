from argparse import ArgumentParser

import pandas as pd
import pkg_resources
import gzip
import json

from smug.connection_manager import ConnectionManager


class GzImporter:
    def __init__(self, connection_mananger):
        self.connection_manager = connection_mananger

    def process_files(self, files):
        for file in files:
            self.process_file(file)

    def process_file(self, file):
        filename = pkg_resources.resource_filename('resources', file)

        with gzip.open(filename, 'rt') as f:
            print('Sending {}'.format(file))
            contents = f.read()

            contents = contents.replace('\n', ',')
            contents = contents.rsplit(',', 1)[0]
            contents = "[{}]".format(contents)

            df = pd.read_json(contents, encoding='records')

            for inex, original_message in df.iterrows():
                formatted_message = {
                    'message': original_message['text'],
                    'author': original_message['user']['name'],
                    'metadata': {
                        'date': str(original_message['timestamp_ms']),
                        'url': original_message['id'],
                        'type': 'post',
                    }
                }
                self.connection_manager.publish_to_queue('cleaning', json.dumps(formatted_message))


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--files', nargs='+')

    args = parser.parse_args()
    files = args.files

    if files is None:
        files = input('Please provide a csv file for processing').split(',')

    connection_manager = ConnectionManager()
    csv_importer = GzImporter(connection_manager)
    csv_importer.process_files(files=files)
    exit(0)
