import h5py
import logging
import pickle
import zlib
import numpy as np

class Snapshotter(object):
    def __init__(self, fname):
        """
        A simple key value pair snapshot util for numpy arrays.
        """
        self.TAG = '[KVP]'
        self.fname = fname
        logging.Logger.setLevel(level=logging.DEBUG)
        logging.info("{} Opening DB {}".format(self.TAG, fname))
        self.db = h5py.File(fname)

    def store(self, k, v):
        logging.info("{} storing {}".format(self.TAG, k))
        v_ = np.void(zlib.compress(pickle.dumps(v, protocol=pickle.HIGHEST_PROTOCOL)))

        if k in self.db:
            logging.error("{} Overwriting group {}!".format(self.TAG, k))
            del self.db[k]

        self.db[k] = [v_]

    def load(self, k):
        return pickle.loads(zlib.decompress(self.db[k][:][0].tostring()))

    def close(self):
        self.db.close()
