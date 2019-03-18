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

import os
import cv2

def stickman(X, Y, param, nodeLowConf, nodeLowConstr=None, edgeLowConf=None, edgeLowConstr=None):
    
    ############################################
    # Extract video properties from original
    ############################################
        
    capture = cv2.VideoCapture(param["AVI_FNAME"])
    fps = cv2.CAP_PROP_FPS
    frameShape = (
        int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)), 
        int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    capture.release()
    
    ############################################
    # Define Constants
    ############################################
    
    COLOR_RED = (255, 0, 0)
    COLOR_GREEN = (0, 255, 0)
    COLOR_BLUE = (0, 0, 255)
  
    FRAME_X_LIM = [0, frameShape[0]] if param["STICKMAN_CROP_X"] is None else param["STICKMAN_CROP_X"]
    FRAME_Y_LIM = [0, frameShape[1]] if param["STICKMAN_CROP_Y"] is None else param["STICKMAN_CROP_Y"]

    pointLocalCoord = lambda iFrame, iNode: (
        int(X[iFrame, iNode] - FRAME_X_LIM[0]),
        int(Y[iFrame, iNode] - FRAME_Y_LIM[0]))
    
    haveNodeConstr = nodeLowConstr is not None
    haveEdges      = edgeLowConf   is not None
    haveEdgeConstr = edgeLowConstr is not None

    ###############
    #  Plot video
    ###############

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    outName = os.path.join(param["REZ_FPATH"], "stickman.avi")
    outWriter = cv2.VideoWriter(outName, fourcc, fps, frameShape, isColor=True)

    for iFrame in range(nRows):
        print("Writing video ["+str(iFrame+1)+'/'+str(nRows)+']\r', end="")

        # Note CV2 column-major
        pic = np.zeros((frameShape[1], frameShape[0], 3), dtype=np.uint8)

        # ------------Draw Nodes----------------
        # If Node has high confidence, draw it
        # Change color if node has bad velocity
        for iNode in range(nNodes):
            if not nodeLowConf[iFrame, iNode]:
                p1 = pointLocalCoord(iFrame, iNode)
                badNode = haveNodeConstr and nodeLowConstr[iFrame, iNode]
                color = COLOR_RED if badNode else COLOR_BLUE
                pic = cv2.circle(pic, p1, 10, COLOR_RED, 2)

        # ------------Draw Edges----------------
        # If Edge has high confidence, draw it
        # Change color if edge has bad length
        if haveEdges:
            for iEdge in range(nEdges):
                p1idx, p2idx = param['EDGE_NODES'][iEdge]

                if not edgeLowConf[iFrame, iEdge]:
                    p1 = pointLocalCoord(iFrame, p1idx)
                    p2 = pointLocalCoord(iFrame, p2idx)
                    badEdge = haveEdgeConstr and edgeLowConstr[iFrame, iNode]
                    color = COLOR_RED if badEdge else COLOR_GREEN
                    pic = cv2.line(pic, p1, p2, COLOR_GREEN, 2)

        outWriter.write(pic)#frame.transpose())  # OPENCV is col-major :(

        # cv2.imshow("cool", pic)
        # cv2.waitKey(0)
        # plt.figure()
        # plt.imshow(pic/255)
        # plt.show()

    # Release everything if job is finished
    outWriter.release()
    cv2.destroyAllWindows()

    print("\nDone!")