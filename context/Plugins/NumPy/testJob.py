#!/bin/env python

import sys

sys.path.append("../..")
sys.path.append("../..")
sys.path.append("../../../LapConfig")
                
from CustomJob import CustomTask

matrixSizes = range(10,1010,10)

def calcSweepValueInt(taskId, sweepSize):
    return matrixSizes[taskId-1]

job = CustomTask()
job.mainFile = "main.py"
job.sweepSize = len(matrixSizes)
job.sweepParams["matrixSize"] = matrixSizes
job.addInputFile("main.py")
job.executable = "python"
job.arguments = "main.py"
job.calculateSweepValueInt = calcSweepValueInt
job.setup()
job.clean()
