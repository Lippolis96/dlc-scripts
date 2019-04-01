import numpy as np
# import pandas as pd
from collections import OrderedDict

def parse_dlc_csv(fname):
    
    # Read file
    f = open(fname, 'r')
    lines = f.readlines()
    f.close()

    # Parse CSV data
    nodeNames = list(OrderedDict.fromkeys(lines[1].strip().split(',')[1:]))
    data = np.array([line.strip().split(',') for line in lines[3:]]).astype(float)
    # df = pd.read_csv(dataFileName, sep=',', header=None, dtype=float, skiprows=3)
    # print("Data shape is", data.shape)
    nNodes = len(nodeNames)
    # nRows = data.shape[0]

    # Extract column positions from header
    bodyparts = np.array(lines[1].strip().split(','))
    properties = np.array(lines[2].strip().split(','))
    colX = np.zeros(nNodes, dtype=int)
    colY = np.zeros(nNodes, dtype=int)
    colP = np.zeros(nNodes, dtype=int)
    for i in range(nNodes):
        thiscols = bodyparts == nodeNames[i]
        colX[i] = np.where(np.logical_and(thiscols, properties == 'x'))[0]
        colY[i] = np.where(np.logical_and(thiscols, properties == 'y'))[0]
        colP[i] = np.where(np.logical_and(thiscols, properties == 'likelihood'))[0]
        
    return nodeNames, data[:, colX], data[:, colY], data[:, colP]