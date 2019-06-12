import numpy as np

# Find all nodes with too low likelihood
def likelihood_constrain(P, param):
    nFrames, nNodes = P.shape
    perr = 1 - P
    return perr, np.greater(perr, param["LIKELIHOOD_THR"])

# Find all nodes with too high velocity
def velocity_constrain(X, Y, nodeLowConf, param):
    nFrames, nNodes = X.shape
    
    # Velocity, confidence and threshold
    V = np.sqrt((X[1:] - X[:-1])**2 + (Y[1:] - Y[:-1])**2)
    VLowConf = nodeLowConf[:-1] & nodeLowConf[1:]
    badV = V > param["NODE_MAX_V"]
    
    # Node has bad velocity with respect to at least one neighbour
    nodeBadV1 = np.zeros(X.shape, dtype=bool)
    print(nodeBadV1.shape, badV.shape)
    nodeBadV1[:-1] |= badV
    nodeBadV1[1:]  |= badV
    
    # Node has bad velocity with respect to both neighbours
    nodeBadV2 = np.ones(X.shape, dtype=bool)
    nodeBadV2[:-1] &= badV
    nodeBadV2[1:]  &= badV
                
    return V, VLowConf, nodeBadV1, nodeBadV2


# Compute edge length, and mark nodes as bad if their length is too low/high
def edge_constrain(X, Y, nodeLowConf, param):
    nFrames, nNodes = X.shape
    nEdges = len(param['EDGE_NODES'])
    edgeLength = np.zeros((nFrames, nEdges))
    edgeLowConf = np.zeros((nFrames, nEdges), dtype=bool)
    edgeBadLength = np.zeros((nFrames, nEdges), dtype=bool) # Edge is bad if its length is too big or too small
    nodeBadEdge = np.zeros(X.shape)
    
    # Maximum number of edges adjacent to each node
    nodeMaxEdgeQuantity = np.zeros(nNodes)
    for edge in param['EDGE_NODES']:
        for nodeIdx in edge:
            nodeMaxEdgeQuantity[nodeIdx] += 1
    
    # Compute edge Lengths 
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
        edgeTooSmall = edgeLength[:, iEdge] < rMin * edgeLenAvg
        edgeTooLarge = edgeLength[:, iEdge] > rMax * edgeLenAvg
        edgeBadLength[:, iEdge] = np.logical_or(edgeTooSmall, edgeTooLarge)
        
        # Edge is confident if both adjacent points are confident
        edgeLowConf[:, iEdge] = np.logical_or(nodeLowConf[:, p1idx], nodeLowConf[:, p2idx])
        
        # Mark all nodes adjacent to this edge as bad
        nodeBadEdge[:, p1idx] += edgeBadLength[:, iEdge]
        nodeBadEdge[:, p2idx] += edgeBadLength[:, iEdge]
        
    # Consider node as bad if it has at least one neighbouring edge and all edges adjacent to it are bad
    for iNode in range(nNodes):
        nodeBadEdge[:, iNode] = (nodeBadEdge[:, iNode] > 0) & (nodeBadEdge[:, iNode] == nodeMaxEdgeQuantity[iNode])
        
    return edgeLength, edgeBadLength, edgeLowConf, nodeBadEdge

# Provide triplet of points for each angle
# def angle_constrain(X, Y, param):
#     nFrames, nNodes = X.shape
#     nAngles = len(param['ANGLE_NODES'])
    
#     angles = np.zeros((nFrames, nAngles))
#     for iAngle in range(nAngles):
#         p_idx = np.array(param['ANGLE_NODES'][iAngle])
#         px = X[:, p_idx]
#         py = Y[:, p_idx]
#         v1 = np.vstack((px[:, 0] - px[:, 1], py[:, 0] - py[:, 1])).T
#         v2 = np.vstack((px[:, 2] - px[:, 1], py[:, 2] - py[:, 1])).T

#         ab_cos = v1[:, 0]*v2[:, 0] + v1[:, 1]*v2[:, 1]
#         ab_sin = v1[:, 0]*v2[:, 1] - v1[:, 1]*v2[:, 0]
#         angles[:, iAngle] = np.arctan2(ab_sin, ab_cos) * 180 / np.pi
        
#     return angles
    
    
    




