#####################
#### DO NOT EDIT ####
#####################

"""
owner: isst.

This file will do offline processing
The 1st parameter should be input file path and the 2nd parameter should be output file path
"""

import sys
from model import ModelImp

def Process(inputPath, outputPath):

    with  open(inputPath, 'r', encoding = 'utf-8', errors='ignore') as inFileHandle:
      with open(outputPath, "w", encoding = 'utf-8', errors='ignore') as outFileHandle:
        model = ModelImp()
        line = inFileHandle.readline()
        line = line.strip()
        while(line):
          result = model.Eval(line)
          outFileHandle.write(result)
          outFileHandle.write("\n")
          line = inFileHandle.readline()
          line = line.strip()


if __name__ == "__main__":
  if(len(sys.argv) < 3):
    raise Exception("Must contains input Path and output Path as first two argumentations")
  Process(sys.argv[1], sys.argv[2])

