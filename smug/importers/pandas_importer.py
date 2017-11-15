import pandas as pd
import hashlib


class PandasImporter:
    dtypes = {
        '72197921735611c48d8114efb03740ce': 'formatter.coosto',
        '52cb34ef57fcb0367ae922ce156dc04c': 'formatter.twinl'
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
                self.connection_manager.publish_to_queue('clean', row.to_json())
