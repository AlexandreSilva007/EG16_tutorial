import h5py
import logging
import pickle
import zlib
import numpy as np
import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.colab import auth
from oauth2client.client import GoogleCredentials
from google.colab import files

class Snapshotter(object):
    def __init__(self, fname):
        """
        A simple key value pair snapshot util for numpy arrays.
        """
        self.TAG = '[KVP]'
        self.fname = fname
        logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')
        logging.info("{} Opening DB {}".format(self.TAG, fname))
        self.db = h5py.File(fname)

    def store(self, k, v):
        logging.info("{} storing {}".format(self.TAG, k))
        v_ = np.void(zlib.compress(pickle.dumps(v, protocol=pickle.HIGHEST_PROTOCOL)))

        if k in self.db:
            logging.error("{} Overwriting group {}!".format(self.TAG, k))
            del self.db[k]

        self.db[k] = [v_]
        
        filename = k+"/pmat.zip"
        print(filename)
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        output_file = open(filename, "wb+")
        pickle.dump([v_], output_file)
        output_file.close()
        
        auth.authenticate_user()
        gauth = GoogleAuth()
        gauth.credentials = GoogleCredentials.get_application_default()
        drive = GoogleDrive(gauth)
        file1 = drive.CreateFile({'title': 'mat.zip'})
        file1.SetContentFile(filename)
        file1.Upload()
        files.download(filename)
                
        #filename = k+"/mat.zip"
        #os.makedirs(os.path.dirname(filename), exist_ok=True)
            
        #newFile = open(k+"/mat.zip", "wb+")
        #newFileByteArray = bytes([v_])
        #newFile.write(newFileByteArray)
        #newFile.close()
        #files.download(k+"/mat.zip")

    def load(self, k):
        return pickle.loads(zlib.decompress(self.db[k][:][0].tostring()))

    def close(self):
        self.db.close()
