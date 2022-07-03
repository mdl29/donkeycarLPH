from donkeycar.parts.tub_v2 import Tub
import logging

class CustomTubWriter(object):
    """
    A Donkey part, which can write records to the datastore.
    """
    def __init__(self):
        self.logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)

        self.base_path = None
        self.inputs = None
        self.types = None
        self.metadata = None
        self.max_catalog_len = None

    def configure(self, base_path, inputs=[], types=[], metadata=[],
                 max_catalog_len=1000):
        self.base_path = base_path
        self.inputs = inputs
        self.types = types
        self.metadata = metadata
        self.max_catalog_len = max_catalog_len

        self.create_tub()

    def create_tub(self):
        """
        Create the tub.
        """
        self.tub = Tub(self.base_path, self.inputs, self.types, self.metadata, self.max_catalog_len)

    def reset(self):
        """
        Simply recreate the tub
        :return:
        """
        self.logger.debug('Resetting / Recreating tub_writer')
        self.create_tub()

    def run(self, *args):
        assert len(self.tub.inputs) == len(args), \
            f'Expected {len(self.tub.inputs)} inputs but received {len(args)}'
        record = dict(zip(self.tub.inputs, args))
        self.tub.write_record(record)
        return self.tub.manifest.current_index

    def __iter__(self):
        return self.tub.__iter__()

    def close(self):
        self.tub.close()

    def shutdown(self):
        self.close()