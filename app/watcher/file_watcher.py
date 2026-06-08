import app.helper.FileHelper as fp
from datetime import datetime as dt
from app.models.file_record import FileRecord
import pprint
import time
class FileWatcher:
    def __init__(self,Dir):
        self.Dir = Dir
        self.Date=dt.now()
    def WatchStart(self):
        while True:
            dc = fp.LoopDirectory(self.Dir)
            for k, v in dc.items():
                print("NEW FILE:", k)

            time.sleep(2)

    
        
    
            
            
    

