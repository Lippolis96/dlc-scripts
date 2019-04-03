import numpy as np

# Find all nodes with too low likelihood
def likelihood_constrain(P, param):
    nFrames, nNodes = P.shape
    perr = 1 - P
    return perr, np.greater(perr, param["LIKELIHOOD_THR"])

# Find all nodes with too high velocity
def velocity_constrain(X, Y, nodeLowConf, param):
    nFrames, nNodes = X.shape
    
    # Velocity
    V = np.sqrt((X[1:] - X[:-1])**2 + (Y[1:] - Y[:-1])**2)
    
    # Confidence of nodes that are used to compute velocity
    VLowConf = np.logical_or(nodeLowConf[1:], nodeLowConf[:-1])
    
    # Compute velocities that exceed respective thresholds
    nodeBadV = np.greater(V - param["NODE_MAX_V"], 0)
    #np.array([V[:, i] > vmax for i, vmax in enumerate(param["NODE_MAX_V"])]).transpose()

    # Ignore low confidence velocities, as they are a priori non-informative
    nodeBadV[VLowConf] = False
    
    # Velocity jumps twice - once to enter bad point, once to exit back on track
    # The latter node should not be marked as bad according to this metric
    # SO: Unmark velocity as too high if
    # 1) Next velocity is normal, and
    # 2) At least two velocities in a row were abnormal
    for iNode in range(nNodes):
        for iFrame in range(3, nFrames):
            if nodeBadV[iFrame-2, iNode] and nodeBadV[iFrame-1, iNode] and not nodeBadV[iFrame, iNode]:
                nodeBadV[iFrame-1, iNode] = False
                
    return V, VLowConf, nodeBadV


# Compute edge length, and mark nodes as bad if their length is too low/high
def edge_constrain(X, Y, nodeLowConf, param):
    nFrames, nNodes = X.shape
    nEdges = len(param['EDGE_NODES'])
    edgeLength = np.zeros((nFrames, nEdges))
    edgeLowConf = np.zeros((nFrames, nEdges), dtype=bool)   # Edge is low-confident if at least one point is low-confident
    edgeBadLength = np.zeros((nFrames, nEdges), dtype=bool) # Edge is bad if its length is too big or too small
    
    for iEdge in range(nEdges):
        p1idx, p2idx = param['EDGE_NODES'][iEdge]
        rMin = param['EDGE_MIN_R'][iEdge]
        rMax = param['EDGE_MAX_R'][iEdge]

        # Compute edge lengths
        DX = X[:, p1idx] - X[:, p2idx]
        DY = Y[:, p1idx] - Y[:, p2idx]
        edgeLength[:, iEdge] = np.sqrt(DX**2 + DY**2)
        edgeLenAvg = np.mean(edgeLength[:, iEdge])
        
        # Mark edges as bad if relative length is too low/high
        edgeTooSmall = np.less(edgeLength[:, iEdge], rMin * edgeLenAvg)
        edgeTooLarge = np.greater(edgeLength[:, iEdge], rMax * edgeLenAvg)
        edgeBadLength[:, iEdge] = np.logical_or(edgeTooSmall, edgeTooLarge)
        
        # # Filter out only edges that are confident
        edgeLowConf[:, iEdge] = np.logical_or(nodeLowConf[:, p1idx], nodeLowConf[:, p2idx])
        # edgeBadLength[edgeLowConf[:, iEdge], iEdge] = False

    return edgeLength, edgeLowConf, edgeBadLength
