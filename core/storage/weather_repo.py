from pathlib import Path
import scipy.io as sio

class WeatherRepository:
    def __init__(self, path):
        self.path = path

    def read_raw_mat(self):
        if not self.path.exists():
            return None
        
        return sio.loadmat(self.path)
