import locale
from argparse import ArgumentParser
import pkg_resources
import gzip
import json
from datetime import datetime

from send_to_smug_helper import SendToSmugHelper


class TwiNLImporter:
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
                self.process_message(original_message=original_message)

    @SendToSmugHelper()
    def process_message(self, original_message):
        try:
            return {
                'message': original_message['text'],
                'author': original_message['user']['name'],
                'metadata': {
                    'date': datetime.fromtimestamp(int(original_message['timestamp_ms']) / 1000),
                    'url': original_message['id'],
                    'type': 'post',
                    'source': 'twitter',
                    'source_import': 'twinl',
                    'lang': locale.normalize('{}.utf-8'.format(original_message['lang']))
                }
            }
        except KeyError:
            print(original_message)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--files', nargs='+')

    args = parser.parse_args()
    files = args.files

    files = [resource for resource in pkg_resources.resource_listdir('resources', '') if
             '.gz' in resource]

    twinl_importer = TwiNLImporter()
    twinl_importer.process_files(files=files, large_analyses=True)
    exit(0)
