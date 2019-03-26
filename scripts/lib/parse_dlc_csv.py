import numpy as np
# import pandas as pd

def parse_dlc_csv(fname, param):
    
    # Read file
    f = open(fname, 'r')
    lines = f.readlines()
    f.close()

    # Parse CSV data
    data = np.array([line.strip().split(',') for line in lines[3:]]).astype(float)
    # df = pd.read_csv(dataFileName, sep=',', header=None, dtype=float, skiprows=3)
    # print("Data shape is", data.shape)
    nNodes = len(param['NODE_NAMES'])
    # nRows = data.shape[0]

    # Extract column positions from header
    bodyparts = np.array(lines[1].strip().split(','))
    properties = np.array(lines[2].strip().split(','))
    colX = np.zeros(nNodes, dtype=int)
    colY = np.zeros(nNodes, dtype=int)
    colP = np.zeros(nNodes, dtype=int)
    for i in range(nNodes):
        thiscols = bodyparts == param['NODE_NAMES'][i]
        colX[i] = np.where(np.logical_and(thiscols, properties == 'x'))[0]
        colY[i] = np.where(np.logical_and(thiscols, properties == 'y'))[0]
        colP[i] = np.where(np.logical_and(thiscols, properties == 'likelihood'))[0]
        
    return data[:, colX], data[:, colY], data[:, colP]