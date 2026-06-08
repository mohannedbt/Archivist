from tkinter.filedialog import askdirectory
import os
import tqdm
import datetime
import pprint
from app.extractors.router import GetSummary
from app.classifiers.rule_classifier import Categorize
from app.models.file_record import FileRecord
legal=[".pdf",".jpeg",".exe",".docx",".txt"]

def convert(epoch):
    epoch_date_time = datetime.datetime.fromtimestamp(epoch)   
    return epoch_date_time
    
def GetDownloadsDirectory():
    DownloadDir='{}'.format(askdirectory())
    return DownloadDir

# Source - https://stackoverflow.com/a/1094933
# Posted by Sridhar Ratnakumar, modified by community. See post 'Timeline' for change history
# Retrieved 2026-06-07, License - CC BY-SA 4.0

def Unitof_fmt(num, suffix="B"):
    for unit in ("", "K", "M", "G", "T", "P", "E", "Z"):
        if abs(num) < 1024.0:
            return f"{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

def FormatSize(n):
  l=len(str(n))
  N=(l//3)*3
  size=n/pow(10,N)
  return size
  
  
def GetFileInfo(filepath,filename):
   fileStats=os.stat(filepath)
   dic={}
   dic["path"]=filepath
   dic["filename"]=filename
   dic["Size"]=FormatSize(fileStats.st_size)
   dic["Unit"]=Unitof_fmt(fileStats.st_size)
   dic["created_at_HR"]=convert(fileStats.st_ctime)
   dic["created_at"]=(fileStats.st_ctime)
   dic["hash"]=hash(filepath)
   dic["Summary"]=GetSummary(filepath)
   dic["Category"]=Categorize(filepath)
   return dic    
def LoopDirectory(Downloaddir: str, Legal=legal):
    DirDic = {}

    for subdir, dirs, files in os.walk(Downloaddir):
        for file in files:

            if FileRecord.get_or_none(FileRecord.filename == file):
                continue

            if not any(file.endswith(l) for l in Legal):
                continue

            filepath = os.path.join(subdir, file)
            dic = GetFileInfo(filepath, file)

            DirDic[file] = dic

            FileRecord.create(
                path=dic["path"],
                filename=dic["filename"],
                created_at=dic["created_at_HR"],
                category=os.path.splitext(file)[1],
                summary="",
                file_hash=str(dic["hash"])
            )

    return DirDic
             
