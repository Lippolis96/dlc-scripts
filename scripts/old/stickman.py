'''
Stickman V1.01
  - ARGV[1] : Gets DLC CSV file with coordinates of 5 joints
  - Computes distances between joints, as well as velocity of each joint
  - Marks joints as bad if their velocity exceeds 70pix / frame
  - Marks distances as bad if they exceed [0.5x, 2.0x] scale of their mean value
  - Report number of bad joints and distances
  - Save video of joints and distances.
    - Change color of joint circle if it is predicted to be bad in this frame
    - Change color of distance line if it is predicted to be bad in this frame

TODO-EXTENSIONS:
  [+] Predict number of nodes, their x,y,p from header
  [+] Enable edge shape template from file
  [+] Study likelihood value p, mark some joints as missing if p too small.
  [+] Enable half-complete limbs in case of missing joints. See if any are actually missing
  [ ] Experiment with threshold. See if there are advices from DLC people
  [ ] Optionally - allow automatic save of all (supposedly) bad frames as images
  [ ] Add angles as a metric. Specify ranges for angles in the file
    [ ] Include virtual joint, ask Pia
  [ ] Consider removing velocity as a test - it does not appear to offer anything more than length already offers
    [+] If keep velocity - fix bug where it always marks one more point than is actually necessary
    [ ] Still some bug - most likely fuck it
  [ ] Ultimate statistics - plot ratio of (bad length frames / all kept frames) as function of cutoff threshold. Thus optimize threshold
  
  [ ] Optionally - enable original video overlay
  [ ] Compare with HDF5 file they save
'''

import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cv2


#########################
# Parse template file
#########################

dataFileName = sys.argv[1]
print("Template file ::: ", dataFileName)

with open(dataFileName) as f:
    temp_dict = json.load(f)

nNodes = len(temp_dict['NODE_NAMES'])
nEdges = len(temp_dict['EDGE_NODES'])


#########################
# Parse CSV file
#########################

print("Template file ::: ", temp_dict['CSV_FULLPATH'])

f = open(temp_dict['CSV_FULLPATH'], 'r')
lines = f.readlines()
f.close()

# Parse CSV data
data = np.array([line.strip().split(',') for line in lines[3:]]).astype(float)
# df = pd.read_csv(dataFileName, sep=',', header=None, dtype=float, skiprows=3)
print("Data shape is", data.shape)
nRows = data.shape[0]

# Extract column positions from header
bodyparts = np.array(lines[1].strip().split(','))
properties = np.array(lines[2].strip().split(','))
colX = np.zeros(nNodes, dtype=int)
colY = np.zeros(nNodes, dtype=int)
colP = np.zeros(nNodes, dtype=int)
for i in range(nNodes):
    thiscols = bodyparts == temp_dict['NODE_NAMES'][i]
    colX[i] = np.where(np.logical_and(thiscols, properties == 'x'))[0]
    colY[i] = np.where(np.logical_and(thiscols, properties == 'y'))[0]
    colP[i] = np.where(np.logical_and(thiscols, properties == 'likelihood'))[0]


#########################
# Statistical analysis of goodness of joints
#########################
# Compute velocity per frame of each tracked point via v(t) = sqrt((x(t+dt) - x(t))^2 + (y(t+dt) - y(t))^2)
#   - Find CDF of velocities for each tracked point, plot it
# Compute length of each joint via L(t) = sqrt((x1(t) - x2(t))^2 + (y1(t) - y2(t))^2)
#   - Plot joint length as a function of time
#   - Compute how many times at least one joint is more than 2 times different from its mean value. Those joints are for sure bad
#########################

'''
Algorithm:
1) Compute velocities for all nodes
2) Compute lengths for all edges
3) Find all nodes that are unconfident
4) Mark velocity as unconfident, if at least one involved node is unconfident
5) Mark edge as unconfident, if at least one involved node is unconfident
6) Set all unconfident velocities to NAN
7) Set all unconfident edge lengths to NAN
'''

isNodeLowConf = np.zeros((nRows, nNodes)).astype(bool)
isEdgeLowConf = np.zeros((nRows, nEdges)).astype(bool)
isNodeHighVelocity = np.zeros((nRows, nNodes)).astype(bool)
isEdgeLengthAbnormal = np.zeros((nRows, nEdges)).astype(bool)

edgeLenAvg = np.zeros(nEdges)



# Compute and plot CDF velocities and likelihoods for each node
fig, ax = plt.subplots(nrows=2, ncols=2)


# Examine confidence distribution of Nodes
frameCDF = np.linspace(nRows, 1, nRows)
for iNode in range(nNodes):
    label = temp_dict['NODE_NAMES'][iNode]
    perr = 1 - data[:, colP[iNode]]
    isNodeLowConf[:, iNode] = perr > temp_dict["LIKELIHOOD_THR"]
    ax[0][0].loglog(np.sort(perr), frameCDF, label=label)

ax[0][0].set_xlabel("1-Likelihood")
ax[0][0].set_ylabel("CDF of number of frames")
ax[0][0].legend()


# Compute Node velocity, and mark nodes as bad if their velocity is too high
for iNode in range(nNodes):
    label = temp_dict['NODE_NAMES'][iNode]
    VMAX = temp_dict['NODE_MAX_V'][iNode]
    X = data[:, colX[iNode]]
    Y = data[:, colY[iNode]]
    VX = X[1:] - X[:-1]
    VY = Y[1:] - Y[:-1]
    VTOT = np.sqrt(VX**2 + VY**2)

    # Filter out only velocities that are confident, and plot their CDF
    isVLowConf = np.logical_or(isNodeLowConf[:-1, iNode], isNodeLowConf[1:, iNode])
    confVelocity = VTOT[np.logical_not(isVLowConf)]
    confFrameCDF = np.linspace(len(confVelocity), 1, len(confVelocity))
    ax[1][0].semilogy(np.sort(confVelocity), confFrameCDF, label=label)
    
    # Mark nodes as bad if velocity is too high
    isNodeHighVelocity[1:, iNode] = VTOT > VMAX
    
    # Velocity jumps twice - once to enter bad point, once to exit back on track
    # The latter node should not be marked as bad according to this metric
    for iFrame in range(2, nRows):
        if (isNodeHighVelocity[iFrame-1, iNode] and not isNodeHighVelocity[iFrame, iNode]):
            isNodeHighVelocity[iFrame-1, iNode] = False
            
    # Ignore high velocity for all nodes that have low confidence
    isNodeHighVelocity[isNodeLowConf[:, iNode], iNode] = False

ax[1][0].set_xlabel("velocity in pixel")
ax[1][0].set_ylabel("CDF of number of frames")
ax[1][0].legend()


# Compute edge length, and mark nodes as bad if their length is too low/high
for iEdge in range(nEdges):
    p1idx, p2idx = temp_dict['EDGE_NODES'][iEdge]
    rMin = temp_dict['EDGE_MIN_R'][iEdge]
    rMax = temp_dict['EDGE_MAX_R'][iEdge]
    
    X1 = data[:, colX[p1idx]]
    Y1 = data[:, colY[p1idx]]
    X2 = data[:, colX[p2idx]]
    Y2 = data[:, colY[p2idx]]
    edgeLen = np.sqrt((X1 - X2)**2 + (Y1 - Y2)**2)
    edgeLenAvg[iEdge] = np.average(edgeLen)    
    
    # Filter out only edges that are confident, and plot their relative lengths
    isEdgeLowConf[:, iEdge] = np.logical_or(isNodeLowConf[:, p1idx], isNodeLowConf[:, p2idx])
    confEdgeLen = edgeLen[np.logical_not(isEdgeLowConf[:, iEdge])]
    ax[0][1].semilogy(confEdgeLen / edgeLenAvg[iEdge], label=str(iEdge))
    
    # Mark edges as bad if relative length is too low/high
    isEdgeLengthAbnormal[:,iEdge] = np.logical_or(edgeLen < rMin * edgeLenAvg[iEdge], edgeLen > rMax * edgeLenAvg[iEdge])
    isEdgeLengthAbnormal[isEdgeLowConf[:, iEdge],iEdge] = False
    
ax[0][1].set_xlabel("frame index")
ax[0][1].set_ylabel("Relative Joint length")
ax[0][1].legend()

plt.show()


print("Average lengths of edges are", edgeLenAvg)
print("Total number of unconfident frames", np.sum(np.sum(isNodeLowConf, axis=1) > 0))
print("Total number of frames with bad velocity", np.sum(np.sum(isNodeHighVelocity, axis=1) > 0))
print("Total number of frames with bad edges", np.sum(np.sum(isEdgeLengthAbnormal, axis=1) > 0))



###########################
### Draw circles and lines, save video
###########################


if temp_dict["AVI_FULLPATH"] == "None":
    FRAME_X_LIM = [100, 750]
    FRAME_Y_LIM = [100, 750]
    frameShape = (
        FRAME_X_LIM[1] - FRAME_X_LIM[0],
        FRAME_Y_LIM[1] - FRAME_Y_LIM[0])
else:
    capture = cv2.VideoCapture(temp_dict["AVI_FULLPATH"])
    frameShape = (
        int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)), 
        int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    capture.release()
    FRAME_X_LIM = [0, frameShape[0]]
    FRAME_Y_LIM = [0, frameShape[1]]


print(frameShape)
print(np.max(data[:, colX]), np.max(data[:, colY]))

# Constants
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 0, 255)

getPoint = lambda iFrame, iNode: (
    int(data[iFrame, colX[iNode]] - FRAME_X_LIM[0]),
    int(data[iFrame, colY[iNode]] - FRAME_Y_LIM[0]))


if temp_dict["RESULT_FULLPATH"] != "None":
    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter(temp_dict["RESULT_FULLPATH"], fourcc, 100.0, frameShape, isColor=True)

    for iFrame in range(nRows):
        print("Writing video ["+str(iFrame+1)+'/'+str(nRows)+']\r', end="")
        
        # Note CV2 column-major
        pic = np.zeros((frameShape[1], frameShape[0], 3), dtype=np.uint8)
        
        # If Node has high confidence, draw it
        # Change color if node has bad velocity
        for iNode in range(nNodes):
            if not isNodeLowConf[iFrame, iNode]:
                p1 = getPoint(iFrame, iNode)

                if isNodeHighVelocity[iFrame, iNode]:
                    pic = cv2.circle(pic, p1, 10, COLOR_RED, 2)
                else:
                    pic = cv2.circle(pic, p1, 10, COLOR_BLUE, 2)

        # If Edge has high confidence, draw it
        # Change color if edge has bad length
        for iEdge in range(nEdges):
            p1idx, p2idx = temp_dict['EDGE_NODES'][iEdge]
            
            if not isEdgeLowConf[iFrame, iEdge]:
                p1 = getPoint(iFrame, p1idx)
                p2 = getPoint(iFrame, p2idx)

                if isEdgeLengthAbnormal[iFrame,iEdge]:
                    pic = cv2.line(pic, p1, p2, COLOR_RED, 2)
                else:
                    pic = cv2.line(pic, p1, p2, COLOR_GREEN, 2)

        out.write(pic)#frame.transpose())  # OPENCV is col-major :(

        # cv2.imshow("cool", pic)
        # cv2.waitKey(0)
        # plt.figure()
        # plt.imshow(pic/255)
        # plt.show()

    # Release everything if job is finished
    out.release()
    cv2.destroyAllWindows()
    
print("\nDone!")

