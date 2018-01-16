import locale
from argparse import ArgumentParser
import pandas as pd
import pkg_resources

from send_to_smug_helper import SendToSmugHelper


class CoostoImporter:
    def __init__(self, large_analysis=False):
        self.large_analysis = large_analysis

    def process_files(self, files):
        for file in files:
            self.process_file(file)

    def process_file(self, file):
        filename = pkg_resources.resource_filename('resources', file)
        print('Sending {}'.format(file))
        df = pd.read_csv(filename, sep=';')
        for index, row in df.iterrows():
            if self.large_analysis:
                if index % 10 != 0:
                    continue
            self.process_message(row)

    @SendToSmugHelper()
    def process_message(self, message):
        formatted_message = {
            'message': message['bericht tekst'],
            'author': message['auteur'],
            'metadata': {
                'date': message['datum'],
                'url': message['url'],
                'type': message['type'],
                'source': 'twitter',
                'source_import': 'coosto',
                'lang': locale.normalize('nl.utf-8')
            }
        }

        if formatted_message['message'] != '':
            return formatted_message


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--files', nargs='+')

    args = parser.parse_args()
    files = args.files

    if files is None:
        files = [resource for resource in pkg_resources.resource_listdir('resources', '') if
                 '.csv' in resource]

    coosto_importer = CoostoImporter()
    coosto_importer.process_files(files=files)
    exit(0)
