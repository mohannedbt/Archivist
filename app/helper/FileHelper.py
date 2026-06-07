from tkinter.filedialog import askdirectory
import os
import tqdm
from extractors.router import GetSummary
from classifiers.rule_classifier import Categorize
Legal=[".pdf",".jpeg",".exe",".docx",".txt"]
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
   dic["created_at"]=fileStats.st_ctime
   dic["hash"]=hash(filepath)
   dic["Summary"]=GetSummary(filepath)
   dic["Category"]=Categorize(filepath)
   return dic    

def LoopDirectory(Downloaddir):
    DirDic={}
    for subdir, dirs, files in tqdm.tqdm(os.walk(Downloaddir)):  
        for file in files:
            for l in Legal:
                if(file.endswith(l)):
                    dic=GetFileInfo(os.path.join(subdir, file),file)
                    DirDic[dic["hash"]]=dic
    return DirDic  
                
if __name__=="__main__":
  dir=GetDownloadsDirectory()
  print(LoopDirectory(dir))