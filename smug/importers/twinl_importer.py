from argparse import ArgumentParser

import pandas as pd
import pkg_resources
import gzip
import json
from datetime import datetime
from bson import json_util
import os

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
            for content in f.readlines():
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

    base = '20170102-{}.out.gz'

    files = [
        base.format('00'),
        base.format('01'),
        base.format('02'),
        base.format('03'),
        base.format('04'),
        base.format('05'),
        base.format('06'),
        base.format('07'),
        base.format('08'),
        base.format('09'),
        base.format('10'),
        base.format('11'),
        base.format('12'),
        base.format('13'),
        base.format('14'),
        base.format('15'),
        base.format('16'),
        base.format('17'),
        base.format('18'),
        base.format('19'),
        base.format('20'),
        base.format('21'),
        base.format('22'),
        base.format('23')
    ]

    if files is None:
        files = input('Please provide a csv file for processing').split(',')

    connection_manager = ConnectionManager()
    csv_importer = GzImporter(connection_manager)
    csv_importer.process_files(files=files)
    exit(0)
