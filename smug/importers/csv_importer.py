from argparse import ArgumentParser
import pandas as pd
import pkg_resources

from smug.connection_manager import ConnectionManager

from smug.importers.pandas_importer import PandasImporter


class CsvImporter(PandasImporter):
    def process_files(self, files):
        """
        Processes a list of files individually
        
        :param files: array of files
        :return: None
        """
        for file in files:
            self.process_file(file)

    def process_file(self, file):
        """
        Process a single file and send results to smug

        :param file: File URI to be read
        :return: None
        """
        filename = pkg_resources.resource_filename('resources', file)
        print('Sending {}'.format(file))
        df = pd.read_csv(filename, sep=';')
        df = df.drop_duplicates(subset='url', keep='first')

        self.process_dataframe(df)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--files', nargs='+')

    args = parser.parse_args()
    files = args.files

    if files is None:
        files = input('Please provide a csv file for processing').split(',')

    connection_manager = ConnectionManager()
    csv_importer = CsvImporter(connection_manager)
    csv_importer.process_files(files=files)
    exit(0)
