import pandas as pd
import hashlib


class PandasImporter:
    dtypes = {
        '72197921735611c48d8114efb03740ce': 'formatter.coosto'
    }

    def __init__(self, connection_mananger):
        self.connection_manager = connection_mananger

    def process_dataframe(self, df: pd.DataFrame):
        dtypes = str(df.dtypes.values)
        dtypes_hash = hashlib.md5(dtypes.encode()).hexdigest()

        try:
            type = self.dtypes[dtypes_hash]
        except KeyError:
            type = None

        for inex, row in df.iterrows():
            if type is not None:
                self.connection_manager.publish_to_exchange(type, row.to_json())
            else:
                self.connection_manager.publish_to_queue('cleaning', row.to_json())
