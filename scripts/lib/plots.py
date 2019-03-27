import numpy as np
import matplotlib.pyplot as plt

def plotPerrCDF(ax, perr, param):
    nRows, nNodes = perr.shape
    frameCDF = np.linspace(nRows, 1, nRows)
    
    for iNode in range(nNodes):
        label = param['NODE_NAMES'][iNode]
        ax.loglog(np.sort(perr[:, iNode]), frameCDF, label=label)

    ax.set_xlabel("1 - Likelihood")
    ax.set_ylabel("CDF of number of frames")
    ax.legend()
    
    
# Find all nodes for which velocity is confident, plot velocity CDF
def plotVelocityCDF(ax, V, VLowConf, param):
    nRows, nNodes = V.shape
    frameCDF = np.linspace(nRows, 1, nRows)
    
    for iNode in range(nNodes):
        VConf = V[np.logical_not(VLowConf[:, iNode]), iNode]
        ax.semilogy(np.sort(VConf), frameCDF, label=param['NODE_NAMES'][iNode])

    ax.set_xlabel("velocity in pixel")
    ax.set_ylabel("CDF of number of frames")
    ax.legend()

# Find all confident edges, plot their relative length distribution
def plotRelEdgeLenDistr(ax, edgeLength, edgeLowConf, param):
    nRows, nEdges = edgeLength.shape
    
    for iEdge in range(nEdges):
        edgeLenConf = edgeLength[np.logical_not(edgeLowConf[:, iEdge]), iEdge]
        edgeLenAvg = np.mean(edgeLenConf)
        ax.semilogy(edgeLenConf / edgeLenAvg, label=str(iEdge))
    
    ax.set_xlabel("frame index")
    ax.set_ylabel("Relative joint length")
    ax.legend()