import numpy as np
import matplotlib.pyplot as plt

def plotPerrCDF(ax, perr, param):
    nFrames, nNodes = perr.shape
    frameCDF = np.linspace(nFrames, 1, nFrames)
    
    for iNode in range(nNodes):
        label = param['NODE_NAMES'][iNode]
        ax.loglog(np.sort(perr[:, iNode]), frameCDF, label=label)

    ax.set_xlabel("1 - Likelihood")
    ax.set_ylabel("CDF of number of frames")
    ax.legend()
    
    
# Find all nodes for which velocity is confident, plot velocity CDF
def plotVelocityCDF(ax, V, VLowConf, param):
    nFrames, nNodes = V.shape
    
    for iNode in range(nNodes):
        VConf = V[np.logical_not(VLowConf[:, iNode]), iNode]
        frameCDF = np.linspace(len(VConf), 1, len(VConf))
        ax.semilogy(np.sort(VConf), frameCDF, label=param['NODE_NAMES'][iNode])

    ax.set_xlabel("velocity in pixel")
    ax.set_ylabel("CDF of number of frames")
    ax.legend()

# Find all confident edges, plot their relative length distribution
def plotRelEdgeLenDistr(ax, edgeLength, edgeLowConf, param):
    nFrames, nEdges = edgeLength.shape
    
    frameIdxs = np.linspace(0, nFrames-1, nFrames)
    for iEdge in range(nEdges):
        selectedFrames = np.logical_not(edgeLowConf[:, iEdge])
        edgeLenConf = edgeLength[selectedFrames, iEdge]
        frameIdxsThis = frameIdxs[selectedFrames]
        label = param['NODE_NAMES'][iEdge] + '-' + param['NODE_NAMES'][iEdge+1]
        ax.plot(frameIdxsThis, edgeLenConf / np.mean(edgeLenConf), label=label)
    
    ax.set_xlabel("frame index")
    ax.set_ylabel("Relative joint length")
    ax.legend()
    
def plotLowConf(ax, nodeLowConf, param):
    nFrames, nNodes = nodeLowConf.shape
    
    for iNode in range(nNodes):
        ax.plot(0.5*nodeLowConf[:, iNode] + nNodes-iNode-1, label=param['NODE_NAMES'][iNode])
        
    ax.get_yaxis().set_visible(False)
    ax.set_xlabel("frame index")
    ax.set_ylabel("Labels")
    #ax.legend()