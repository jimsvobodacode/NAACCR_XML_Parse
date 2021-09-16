import os, re
import logging
from datetime import datetime

class Utility:

    # configure default python logging
    def ConfigureLogging(self):
        path = os.getcwd() + '\logs'
        if not os.path.exists(path):
            os.makedirs(path)
        path = path + '\\logfile_{:%Y%m%d}.txt'.format(datetime.now())
        logging.basicConfig(filename=path, 
        level=logging.DEBUG, format='%(asctime)s %(message)s')
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        logging.getLogger().addHandler(ch)
    
