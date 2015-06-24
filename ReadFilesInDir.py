import os
import sys
from ReadLSR import readLSRFile

def readFiles(directory):
    for dirname, dirnames, filenames in os.walk(directory): 
        # print path to all filenames.
        for filename in filenames:
            path = os.path.join(dirname, filename)
            readLSRFile(path)
  
if __name__=="__main__":
    dirLocation = sys.argv[1]
    readFiles(dirLocation)